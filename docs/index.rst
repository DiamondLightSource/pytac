Python Toolkit for Accelerator Controls
=======================================

Python Toolkit for Accelerator Controls (Pytac) is a Python library for working
with elements of particle accelerators, developed at Diamond Light Source.

It is hosted on Github at: https://github.com/dls-controls/pytac

Two pieces of software influenced its design:

* Matlab Middlelayer, used widely by accelerator physicists.
* APHLA, high-level applications written in Python by the NSLS-II accelerator
  physics group.


Overview
========

Pytac provides a Python library, ``pytac``, that makes it easier to communicate
with machine hardware for online applications. Although it currently works with
EPICS, it should be possible to adapt to support other control systems.

The design is based around a ``Lattice`` object that contains a sequence of
``Element`` s. Each element represents a physical component in the accelerator,
such as an electromagnet, drift, or BPM. Each element may have zero or more
'fields', each representing a parameter of the component that may change e.g. a
BPM element has fields 'x' and 'y' that represent the beam position, and a
quadrupole magnet has 'b1' that represents the quadrupolar magnetic field. Each
field has one ``Device`` object for monitoring and control purposes, these
devices contain the necessary information to get and set parameter data using
the control system.

Elements may be grouped into families (an element may be in more than one
family), and requested from the lattice object in those families. The current
control system integrates with EPICS and uses EPICS PV (process variable)
objects to tell EPICS which IOC (input/output controller - an EPICS server 
process) to communicate with.
The type of the PV specifies which operations can be performed, there are two
types of PV: readback, which can only be used to retrieve data; and setpoint,
which can be used to set a value as well as for retrieving data. A single
component may have both types; and so some methods take 'handle' as an
argument, this is to tell the control system which PV to use when interfacing
with EPICS, readback (``pytac.RB``) or setpoint (``pytac.SP``).

.. sidebar:: An example control structure.

    .. image:: control_structure.png
       :width: 400

Data may be set to or retrieved from different data sources, from the live
machine (``pytac.LIVE``) or from a simulator (``pytac.SIM``). By default the
'live' data source is implemented using
`Cothread <https://github.com/dls-controls/cothread>`_ to communicate with
EPICS, as described above. The 'simulation' data source is left unimplemented,
as Pytac does not include a simulator. However, ATIP, a module designed to
integrate the `Accelerator Toolbox <https://github.com/atcollab/at>`_ simulator
into Pytac can be found `here. <https://github.com/dls-controls/atip>`_

Data may also be requested or sent in engineering (``pytac.ENG``) or physics
(``pytac.PHYS``) units and will be converted as appropriate. This conversion is
a fundamental part of how Pytac integrates with the physical accelerator, as
physics units are what our description of the accelerator works with (e.g. the
magnetic field inside a magnet) and engineering units are what the IOCs on the
physical components use (e.g. the current in a magnet). Two types of unit
conversion are available: 

* Polynomial (``PolyUnitConv``; often used for linear
  conversion);
* Piecewise Cubic Hermite Interpolating Polynomial
  (``PchipUnitConv``; often used for magnet data where field may not be linear
  with current). 

In the case that measurement data (used to set up the conversion
objects) is not in the same units as the physical models, further functions may
be given to these objects to complete the conversion correctly.

Models of accelerators, physical or simulated, are defined using a set of
``.csv`` files, located by default in the ``pytac/data`` directory. Each model
should be saved in its own directory i.e. different models of the same
accelerator should be separate, just as models of different accelerators would
be.

Contents:
=========

.. toctree::
   :maxdepth: 4

   self
   examples
   developers
   pytac


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
