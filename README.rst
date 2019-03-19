.. image:: https://travis-ci.org/dls-controls/pytac.png
   :target: https://travis-ci.org/dls-controls/pytac
.. image:: https://coveralls.io/repos/github/dls-controls/pytac/badge.svg?branch=master
   :target: https://coveralls.io/github/dls-controls/pytac?branch=master
.. image:: https://landscape.io/github/dls-controls/pytac/master/landscape.svg?style=flat
   :target: https://landscape.io/github/dls-controls/pytac/
.. image:: https://readthedocs.org/projects/pytac/badge/?version=latest
   :target: http://pytac.readthedocs.io/en/latest/?badge=latest
.. image:: https://badge.fury.io/py/pytac.svg
   :target: https://badge.fury.io/py/pytac
.. image:: https://img.shields.io/pypi/pyversions/pytac.svg
   :target: https://badge.fury.io/py/pytac


Python Toolkit for Accelerator Controls (Pytac) is a Python library for working with elements of particle accelerators.

Documentation is available at Readthedocs_.

.. _ReadTheDocs: http://pytac.readthedocs.io

Testing
=======

It is simplest to work with pipenv::

 $ pipenv install --dev
 $ pipenv shell

To run the tests::

 $ python -m pytest

To see a coverage report, check pytest-cov::

 $ python -m pytest --cov-report term-missing --cov=pytac

To build the documentation::

 $ cd docs
 $ sphinx-build -b html -E . _build/html

The documentation is built inside _build/html.

Uploading to Pypi
=================

Create a source distribution::

 $ python setup.py sdist

Build a universal wheel::

 $ python setup.py bdist_wheel

Then upload it using twine::

 $ twine upload dist/*
