import subprocess
import uuid
import os
import tempfile
import json

import pytest
import six


DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def check_output(*arg, **kwargs):
  ret = subprocess.check_output(*arg, **kwargs)
  return ret.decode('utf8')


def test_a():
  secret = str(uuid.uuid4())
  subprocess.call('gcreds put test_a %s' % secret, cwd=DIR_PATH, shell=True)
  secret_get = check_output('gcreds get test_a', cwd=DIR_PATH, shell=True)
  assert secret_get.strip() == secret


def test_b():
  secret = str(uuid.uuid4())
  d = {'let': 'us', 'have': 'a', 'json': 'file', 'here': '!'}
  with tempfile.NamedTemporaryFile('wb') as f:
    f.write(json.dumps(d).encode('utf8'))
    f.flush()

    subprocess.call('gcreds put test_b < %s' % f.name, cwd=DIR_PATH, shell=True)
    secret_get = check_output('gcreds get test_b', cwd=DIR_PATH, shell=True)
    assert secret_get.strip() == json.dumps(d)


def test_c():
  secret = str(uuid.uuid4())
  with pytest.raises(subprocess.CalledProcessError) as ex:
    secret_get = check_output(
        'gcreds get test_not_set', stderr=subprocess.STDOUT,
        cwd=DIR_PATH, shell=True)

  assert ex.value.returncode == 1
  assert 'test_not_set is not set.' in ex.value.output.strip()
