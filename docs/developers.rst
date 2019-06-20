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
    Python 2.7.3 (default, Nov  9 2013, 21:59:00)
    [GCC 4.4.7 20120313 (Red Hat 4.4.7-3)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>


- Import Pytac and initialise the lattice from the ``VMX`` directory::

    >>> import pytac.load_csv
    >>> lattice = pytac.load_csv.load('VMX')


The ``lattice`` object is used for interacting with elements of the accelerator.
