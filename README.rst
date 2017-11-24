.. image:: https://travis-ci.org/simkimsia/UtilityBehaviors.png
   :target: https://travis-ci.org/simkimsia/UtilityBehaviors
.. image:: https://coveralls.io/repos/github/willrogers/pytac/badge.svg?branch=master
   :target: https://coveralls.io/github/willrogers/pytac?branch=master
.. image:: https://landscape.io/github/willrogers/pytac/master/landscape.svg?style=flat
   :target: https://landscape.io/github/willrogers/pytac/
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

It is simplest to work with a virtualenv.  Then::

 $ pip install -r requirements/local.txt
 $ python -m pytest

To see a coverage report, check pep8 and pyflakes::

 $ python -m pytest --cov=pytac --pep8 --flakes

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
