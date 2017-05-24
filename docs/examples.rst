Examples
********

Print BPM pvs along with s position
-----------------------------------

- Import 'pytac':

     >>> import pytac.load_csv
     >>> import pytac.epics

- Initialize the VMX mode:

     >>> lattice = pytac.load_csv.load('VMX', pytac.epics.EpicsControlSystem())

- Version 1: Get the BPM elements:

     >>> bpms = lattice.get_elements('BPM')

- Print the values of the readback pvs on the b1 field:

     >>> for bpm in bpms:
     >>>    print(bpm.get_pv_name('x', 'readback'), bpm.get_pv_name('y', 'readback'), 'S position', lattice.get_s(bpm))
     ('SR01C-DI-EBPM-01:SA:X', 'SR01C-DI-EBPM-01:SA:Y', 'S position', 4.38)
     ('SR01C-DI-EBPM-02:SA:X', 'SR01C-DI-EBPM-02:SA:Y', 'S position', 8.806500000000002)
     ('SR01C-DI-EBPM-03:SA:X', 'SR01C-DI-EBPM-03:SA:Y', 'S position', 11.374000000000002)
     ('SR01C-DI-EBPM-04:SA:X', 'SR01C-DI-EBPM-04:SA:Y', 'S position', 12.559000000000005)
     ('SR01C-DI-EBPM-05:SA:X', 'SR01C-DI-EBPM-05:SA:Y', 'S position', 14.942500000000006)...

- Version 2 - to get the pv name of each bpm:
     >>> lattice.get_family_pvs('BPM', 'x', 'readback')
     ['SR01C-DI-EBPM-01:SA:X',
     'SR01C-DI-EBPM-02:SA:X',
     'SR01C-DI-EBPM-03:SA:X'
     ...
     >>> lattice.get_family_pvs('BPM', 'y', 'readback')
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
---------------------------------------

- Import 'pytac'

     >>> import pytac

- Initialize the VMX mode

     >>> lattice = pytac.load_csv.load('VMX', pytac.epics.EpicsControlSystem())

- Version 1: Get the Quad elements and print their readback values on the b1 field:

     >>> quads = lattice.get_elements('QUAD')
     >>> for quad in quads:
     >>>    print(quad.get_pv_value('b1', 'readback'))
     71.3240509033
     129.351394653
     98.2537231445
     ...


- Version 2: Print the quad pv values on the b1 field using the lattice. This is more efficient:

     >>> lattice.get_family_values('QUAD', 'b1', 'readback')
     [71.32496643066406,
      129.35191345214844,
      98.25287628173828,
     ...

Print pv names to file
----------------------

- Import 'pytac' and epics:

     >>> import pytac.load_csv
     >>> import pytac.epics

- Initialize the VMX mode:

     >>> lattice = pytac.load_csv.load('VMX', pytac.epics.EpicsControlSystem())

- Version 1: Get the Quad elements individually:

     >>> q1b = lattice.get_elements('Q1B')

- Print the pvs to file:

     >>> with open('elements_in_families.txt', 'a') as out_file:
     >>>    for quad in q1b:
     >>>       pv_name = quad.get_pv_name('b1', 'readback').split(':')[0]
     >>>       out_file.write("{}\n".format(pv_name))
     SR01A-PC-Q1B-10
     SR03A-PC-Q1B-01
     SR03A-PC-Q1B-10
     ...


- Version 2: Get the Quad elements using the lattice:

     >>> with open('elements_in_families.txt', 'a') as out_file:
     >>>     out_file.write('{}'.format(lattice.get_family_pvs('Q1B', 'b1', 'readback')))
     ['SR01A-PC-Q1B-10:I', 'SR03A-PC-Q1B-01:I', 'SR03A-PC-Q1B-10:I']
     ...
