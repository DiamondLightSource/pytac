.. image:: https://github.com/dls-controls/pythonSoftIOC/workflows/Code%20CI/badge.svg?branch=master
   :target: https://github.com/dls-controls/pythonSoftIOC/actions?query=workflow%3A%22Code+CI%22
.. image:: https://codecov.io/gh/dls-controls/pytac/branch/master/graph/badge.svg?token=be222kVyRP
   :target: https://codecov.io/gh/dls-controls/pytac
.. image:: https://readthedocs.org/projects/pytac/badge/?version=latest
   :target: http://pytac.readthedocs.io/en/latest/?badge=latest
.. image:: https://badge.fury.io/py/pytac.svg
   :target: https://badge.fury.io/py/pytac
.. image:: https://img.shields.io/pypi/pyversions/pytac.svg
   :target: https://badge.fury.io/py/pytac
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black


Python Toolkit for Accelerator Controls (Pytac) is a Python library for working
with elements of particle accelerators.

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

To see style violations, use flake8::

 $ flake8

To build the documentation::

 $ cd docs
 $ sphinx-build -b html -E . _build/html

The documentation is built inside _build/html.

Uploading to Pypi
=================

Ensure that the version is correct in `setup.py` and then make a tag that
is the same as the version.

Create a source distribution::

 $ python setup.py sdist

Build a universal wheel::

 $ python setup.py bdist_wheel

Then upload it using twine::

 $ twine upload dist/*
