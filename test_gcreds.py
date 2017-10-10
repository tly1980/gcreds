import subprocess
import uuid
import os
import tempfile
import json

import six


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def check_output(*arg, **kwargs):
  ret = subprocess.check_output(*arg, **kwargs)
  return ret.decode('utf8')


def test_a():
  secret = str(uuid.uuid4())
  subprocess.call('./gcreds.py put test_a %s' % secret, cwd=DIR_PATH, shell=True)
  secret_get = check_output('./gcreds.py get test_a', cwd=DIR_PATH, shell=True)
  assert secret_get.strip() == secret


def test_b():
  secret = str(uuid.uuid4())
  d = {'let': 'us', 'have': 'a', 'json': 'file', 'here': '!'}
  with tempfile.NamedTemporaryFile('wb') as f:
    f.write(json.dumps(d).encode('utf8'))
    f.flush()

    subprocess.call('./gcreds.py put test_b < %s' % f.name, cwd=DIR_PATH, shell=True)
    secret_get = check_output('./gcreds.py get test_b', cwd=DIR_PATH, shell=True)
    assert secret_get.strip() == json.dumps(d)
