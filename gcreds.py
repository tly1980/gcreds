#!/usr/bin/env python
from __future__ import print_function
import argparse
import base64
import io
import sys

from google.cloud import datastore
import googleapiclient.discovery
import six


__version__ = '0.1.3'


AP = argparse.ArgumentParser()
AP.add_argument('--key_ring_id', default='gcreds', type=str, help='KMS KeyRing Id')
AP.add_argument('--crypto_key_id', default='gcreds', type=str, help='KMS CryptoKey Id')
AP.add_argument('--location_id', default='global', type=str, help='KMS Location ID')
AP.add_argument('--project_id', default=None, type=str, help='Project ID')
AP.add_argument('action', type=str, help='Action. Put / Get')
AP.add_argument('name', type=str, help='The name of credential.')
AP.add_argument('plaintext', type=str, nargs='?', help='To be encrypted.')


KEY_KIND = 'Credential'


def encrypt(project_id, location_id, key_ring_id, crypto_key_id, plaintext):
  """Encrypts data from plaintext_file_name using the provided CryptoKey and
  saves it to ciphertext_file_name so it can only be recovered with a call to
  decrypt.
  """

  # Creates an API client for the KMS API.
  kms_client = googleapiclient.discovery.build('cloudkms', 'v1')

  # The resource name of the CryptoKey.
  name = 'projects/{}/locations/{}/keyRings/{}/cryptoKeys/{}'.format(
      project_id, location_id, key_ring_id, crypto_key_id)

  # Use the KMS API to encrypt the data.
  crypto_keys = kms_client.projects().locations().keyRings().cryptoKeys()
  request = crypto_keys.encrypt(
      name=name,
      body={'plaintext': base64.b64encode(plaintext.encode('utf8')).decode('utf8')}
  )
  response = request.execute()
  return response['ciphertext'].encode('utf8')


def decrypt(project_id, location_id, key_ring_id, crypto_key_id, ciphertext_b64):
  """Decrypts data from ciphertext_file_name that was previously encrypted
  using the provided CryptoKey and saves it to plaintext_file_name."""

  # Creates an API client for the KMS API.
  kms_client = googleapiclient.discovery.build('cloudkms', 'v1')

  # The resource name of the CryptoKey.
  name = 'projects/{}/locations/{}/keyRings/{}/cryptoKeys/{}'.format(
      project_id, location_id, key_ring_id, crypto_key_id)

  # Use the KMS API to decrypt the data.
  crypto_keys = kms_client.projects().locations().keyRings().cryptoKeys()
  if six.PY3:
    ciphertext_b64 = ciphertext_b64.decode('utf8')

  request = crypto_keys.decrypt(
      name=name,
      body={'ciphertext': ciphertext_b64})
  response = request.execute()
  ret = base64.b64decode(response['plaintext'].encode('utf8'))

  if six.PY3:
    ret = ret.decode('utf8')

  return ret


def put(project_id, location_id, key_ring_id, crypto_key_id, name, plaintext):
  datastore_client = datastore.Client(project=project_id, namespace='gcreds')
  key = datastore_client.key(KEY_KIND, name)
  creds = datastore.Entity(key=key, exclude_from_indexes=['content'])
  creds['content'] = encrypt(
      project_id, location_id, key_ring_id, crypto_key_id, plaintext)
  datastore_client.put(creds)


def get(project_id, location_id, key_ring_id, crypto_key_id, name):
  datastore_client = datastore.Client(project=project_id, namespace='gcreds')
  key = datastore_client.key(KEY_KIND, name)
  entity = datastore_client.get(key)
  encrypted = entity['content']
  return decrypt(project_id, location_id, key_ring_id, crypto_key_id, encrypted)


def main(args):
  project_id = args.project_id
  if not project_id:
    client = datastore.Client()
    project_id = client.project
    print(
        'project_id is not provided, will use default project: [%s] instead.'
        % project_id, file=sys.stderr)

  if args.action == 'put':
    plaintext = sys.stdin.read() if not args.plaintext else args.plaintext

    if not plaintext:
      sys.exit('Please provide a text to be encrypted.')

    put(project_id, args.location_id, args.key_ring_id, args.crypto_key_id,
        args.name, plaintext)
  else:
    print(
        get(
            project_id, args.location_id, args.key_ring_id,
            args.crypto_key_id, args.name
        )
    )

if __name__ == '__main__':
  main(AP.parse_args())
