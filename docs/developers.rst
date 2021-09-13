Developers
==========

The installation and initialisation steps are slightly different if you want to
work on Pytac. N.B. This guide uses pipenv but a virtualenv will also work.


Installation
~~~~~~~~~~~~

This is only required on your first use.

- Ensure you have the following requirements: Pip, Pipenv, and a local copy of
  Pytac.

- Install dev-packages and Cothread for EPICS support::

    $ pipenv install --dev
    $ pip install cothread
    $ # Cothread is required for EPICS functionality, but Pytac can run without it.


Initialisation
~~~~~~~~~~~~~~

This is required each time you want to start up Pytac.

- Navigate to your ``pytac`` directory and activate a Pipenv shell, and start
  Python::

    $ cd <directory-path>
    $ pipenv shell
    $ python
    Python 3.7.2 (default, Jan 20 2020, 11:03:41)
    [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>


- Import Pytac and initialise the lattice from the ``VMX`` directory::

    >>> import pytac.load_csv
    >>> lattice = pytac.load_csv.load('VMX')


The ``lattice`` object is used for interacting with elements of the accelerator.
