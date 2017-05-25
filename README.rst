.. image:: https://travis-ci.org/simkimsia/UtilityBehaviors.png
   :target: https://travis-ci.org/simkimsia/UtilityBehaviors
.. image:: https://coveralls.io/repos/github/willrogers/pytac/badge.svg?branch=master
   :target: https://coveralls.io/github/willrogers/pytac?branch=master
.. image:: https://landscape.io/github/willrogers/pytac/master/landscape.svg?style=flat
   :target: https://landscape.io/github/willrogers/pytac/
.. image:: https://readthedocs.org/projects/pytac/badge/?version=latest
  :target: http://pytac.readthedocs.io/en/latest/?badge=latest


Python Toolkit for Accelerator Controls (Pytac) is a Python library intended to make it easy to work with particle accelerators.

Testing
=======

It is simplest to work with a virtualenv.  Then:

 >>> pip install -r requirements/local.txt
 >>> export PYTHONPATH=.
 >>> py.test test

To see a coverage report:

 >>> py.test --cov=pytac test

To build documentation correctly:

 >>> cd docs`
 >>> sphinx-build -b html -E . _build/html

The documentation is built inside _build/html.
