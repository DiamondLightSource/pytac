========
Examples
========

Initialisation
~~~~~~~~~~~~~~

- Install pytac and cothread for EPICS support, and start Python::

    $ pip install pytac
    $ pip install cothread
    $ python
    Python 2.7.3 (default, Nov  9 2013, 21:59:00)
    [GCC 4.4.7 20120313 (Red Hat 4.4.7-3)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

- Import 'pytac' and initialise the ``VMX`` ring mode::

    >>> import pytac.load_csv
    >>> lattice = pytac.load_csv.load('VMX')

The ``lattice`` object is used for interacting with elements of the accelerator.

Print BPM pvs along with s position
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Get elements representing BPMs::

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

    >>> lattice.get_pv_names('BPM', 'x', pytac.RB)
    ['SR01C-DI-EBPM-01:SA:X',
    'SR01C-DI-EBPM-02:SA:X',
    'SR01C-DI-EBPM-03:SA:X'
    ...
    >>> lattice.get_pv_names('BPM', 'y', pytac.RB)
    ['SR01C-DI-EBPM-01:SA:Y',
    'SR01C-DI-EBPM-02:SA:Y',
    'SR01C-DI-EBPM-03:SA:Y',
    ...
    >>> lattice.get_family_s('BPM')
    [4.38,
     8.806500000000002,
     11.374000000000002,
     ...

Get the pv value from the quad elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Get the Quad elements and print their readback values on the b1 field::

    >>> quads = lattice.get_elements('QUAD')
    >>> for quad in quads:
    >>>    print(quad.get_value('b1', pytac.RB))
    71.3240509033
    129.351394653
    98.2537231445
    ...


- Print the quad pv values on the b1 field using the lattice. This is more efficient
  since it uses only one request to the control system::

    >>> lattice.get_values('QUAD', 'b1', pytac.RB)
    [71.32496643066406,
     129.35191345214844,
     98.25287628173828,
    ...
