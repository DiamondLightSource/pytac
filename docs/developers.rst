Developers
==========

The installation and initialiseation steps are slightly different if you want to work on pytac.


Installation
~~~~~~~~~~~~

This is only required on your first use.

- Ensure you have the following requirements: Pip, Pipenv, and a local copy of pytac.

- Install dev-packages and cothread for EPICS support::

    $ pipenv install --dev
    $ pip install cothread	# cothread is required for EPICS functionality, but pytac can run without it.


Initialisation
~~~~~~~~~~~~~~

This is required each time you want to start up pytac.

- Navigate to your pytac directory and activate a Pipenv shell, and start Python::

    $ cd <directory-path>
    $ pipenv shell
    $ python
    Python 2.7.3 (default, Nov  9 2013, 21:59:00)
    [GCC 4.4.7 20120313 (Red Hat 4.4.7-3)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>


- Import pytac and initialise from the ``VMX`` ring model::

    >>> import pytac.load_csv
    >>> lattice = pytac.load_csv.load('VMX')


The ``lattice`` object is used for interacting with elements of the accelerator.
