README.rst: README.md
	pandoc --from=markdown --to=rst --output=README.rst README.md

package: README.rst
	python setup.py bdist_wheel --universal