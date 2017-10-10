DEV_ENV := py27

README.rst: README.md
	pandoc --from=markdown --to=rst --output=README.rst README.md

package: README.rst
	python setup.py bdist_wheel --universal

test:
	#export PATH=bin:$$PATH; echo "aa $$PATH"; which gcreds
	tox -e $(DEV_ENV)

tox:
	tox -v

pypi: package
	python setup.py upload -r pypi