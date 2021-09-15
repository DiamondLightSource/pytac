Examples
========

Installation
~~~~~~~~~~~~

This is only required on your first use.

- Ensure you have Pip, then install Pytac and Cothread::

    $ pip install pytac
    $ pip install cothread
    $ # Cothread is required for EPICS functionality, but Pytac can run without it.


Initialisation
~~~~~~~~~~~~~~

This is required each time you want to start up Pytac.

- Navigate to your Pytac directory and start Python::

    $ cd <directory-path>
    $ python
    Python 3.7.2 (default, Jan 20 2020, 11:03:41)
    [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>


- Import Pytac and initialise the lattice from the ``VMX`` directory::

    >>> import pytac.load_csv
    >>> lattice = pytac.load_csv.load('VMX')


The ``lattice`` object is used for interacting with elements of the accelerator.

Print BPM PV names along with s position
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Get all elements that represent ``BPM`` s::

    >>> bpms = lattice.get_elements('BPM')

- Print the device names and s position of each BPM::

    >>> for bpm in bpms:
    >>>    print('BPM {} at position {}'.format(bpm.get_device('x').name, bpm.s))
    BPM SR01C-DI-EBPM-01 at position 4.38
    BPM SR01C-DI-EBPM-02 at position 8.8065
    BPM SR01C-DI-EBPM-03 at position 11.374
    BPM SR01C-DI-EBPM-04 at position 12.559
    BPM SR01C-DI-EBPM-05 at position 14.9425
    ...

- Get PV names and positions for BPMs directly from the lattice object::

    >>> lattice.get_element_pv_names('BPM', 'x', pytac.RB)
    ['SR01C-DI-EBPM-01:SA:X',
    'SR01C-DI-EBPM-02:SA:X',
    'SR01C-DI-EBPM-03:SA:X'
    ...
    >>> lattice.get_element_pv_names('BPM', 'y', pytac.RB)
    ['SR01C-DI-EBPM-01:SA:Y',
    'SR01C-DI-EBPM-02:SA:Y',
    'SR01C-DI-EBPM-03:SA:Y',
    ...
    >>> lattice.get_family_s('BPM')
    [4.38,
    8.806500000000002,
    11.374000000000002,
    ...

Get the value of the 'b1' field of the quad elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Get all Quadrupole elements and print their 'b1' field read back values::

    >>> quads = lattice.get_elements('Quadrupole')
    >>> for quad in quads:
    >>>    print(quad.get_value('b1', pytac.RB))
    71.3240509033
    129.351394653
    98.2537231445
    ...


- Print the ``Quadrupole`` read back values of the 'b1' field using the lattice. This
  is more efficient since it uses only one request to the control system::

    >>> lattice.get_element_values('Quadrupole', 'b1', pytac.RB)
    [71.32496643066406,
    129.35191345214844,
    98.25287628173828,
    ...

Tutorial
~~~~~~~~

For an introduction to pytac concepts and finding your way around, 
an interactive tutorial is available using Jupyter Notebook. Take a look in the
``jupyter`` directory - the ``README.rst`` there describes how to access the tutorial.
