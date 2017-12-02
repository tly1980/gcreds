#!/usr/bin/env python
from __future__ import print_function
import argparse
import base64
import io
import sys
import logging

from google.cloud import datastore
import googleapiclient.discovery
import six


__version__ = '0.2.1'

DEFAULT_KEY_RING_ID = 'gcreds'
DEFAULT_CRYPTO_KEY_ID = 'gcreds'
DEFAULT_LOCATION_ID = 'global'


AP = argparse.ArgumentParser()
AP.add_argument(
    '--key_ring_id',
    default=DEFAULT_KEY_RING_ID, type=str, help='KMS KeyRing Id')
AP.add_argument(
    '--crypto_key_id',
    default=DEFAULT_CRYPTO_KEY_ID, type=str, help='KMS CryptoKey Id')
AP.add_argument(
    '--location_id',
    default=DEFAULT_LOCATION_ID, type=str, help='KMS Location ID')
AP.add_argument('--project_id', default=None, type=str, help='Project ID')
AP.add_argument('action', type=str, help='Action. Put / Get')
AP.add_argument('name', type=str, nargs='?', help='The name of credential.')
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


def get_current_project_id(project_id):
  if not project_id:
    client = datastore.Client()
    project_id = client.project

  return project_id


def put(project_id, name, plaintext,
        location_id=DEFAULT_LOCATION_ID,
        key_ring_id=DEFAULT_KEY_RING_ID, crypto_key_id=DEFAULT_CRYPTO_KEY_ID):
  datastore_client = datastore.Client(project=project_id, namespace='gcreds')
  key = datastore_client.key(KEY_KIND, name)
  creds = datastore.Entity(key=key, exclude_from_indexes=['content'])
  creds['content'] = encrypt(
      project_id, location_id, key_ring_id, crypto_key_id, plaintext)
  datastore_client.put(creds)


def get(project_id, name,
        location_id=DEFAULT_LOCATION_ID,
        key_ring_id=DEFAULT_KEY_RING_ID, crypto_key_id=DEFAULT_CRYPTO_KEY_ID):
  datastore_client = datastore.Client(project=project_id, namespace='gcreds')
  key = datastore_client.key(KEY_KIND, name)

  entity = datastore_client.get(key)
  if not entity:
    return None

  encrypted = entity['content']
  return decrypt(project_id, location_id, key_ring_id, crypto_key_id, encrypted)


def list_creds(project_id):
  datastore_client = datastore.Client(project=project_id, namespace='gcreds')
  return [c.key.name for c in datastore_client.query(kind=KEY_KIND).fetch()]


def main(args):
  # to silent the warnning:
  #    ImportError: file_cache is unavailable when using oauth2client >= 4.0.0
  logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
  project_id = get_current_project_id(args.project_id)
  if not args.project_id:
    print(
        'project_id is not provided, will use default project: [%s] instead.'
        % project_id, file=sys.stderr)

  if args.action == 'put':
    plaintext = sys.stdin.read() if not args.plaintext else args.plaintext

    if not plaintext:
      sys.exit('Please provide a text to be encrypted.')

    put(project_id, args.name, plaintext,
        location_id=args.location_id,
        key_ring_id=args.key_ring_id,
        crypto_key_id=args.crypto_key_id)
  elif args.action == 'get':
    secret = get(
        project_id, args.name, location_id=args.location_id,
        key_ring_id=args.key_ring_id, crypto_key_id=args.crypto_key_id
    )
    if secret:
      print(secret)
    else:
      print('%s is not set.' % args.name, file=sys.stderr)
      sys.exit(1)
  elif args.action == 'list':
    print('You have following credentials:')
    for n in sorted(list_creds(project_id)):
      print('  %s' % n)


if __name__ == '__main__':
  main(AP.parse_args())
