DEV_ENV := py27
PY_IMG:=$(shell python2 -c "import urllib, setup; print urllib.quote('python-{}-blue.svg'.format(' '.join(setup.PY_VERSIONS)))")

README.md: _README.md
	echo "![supported python versions]($(PY_IMG))" > README.md
	cat _README.md >> README.md

README.rst: README.md
	pandoc --from=markdown --to=rst --output=README.rst README.md

package: README.rst

	python setup.py bdist_wheel --universal

test:
	#export PATH=bin:$$PATH; echo "aa $$PATH"; which gcreds
	tox -e $(DEV_ENV)

tox:
	tox -v

pypi: README.rst
	python setup.py bdist_wheel --universal upload -r pypi