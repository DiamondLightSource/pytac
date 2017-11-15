Python Toolkit for Accelerator Controls
=======================================

Python Toolkit for Accelerator Controls (Pytac) is a Python library for working with elements of particle accelerators.

It is hosted on Github at https://github.com/willrogers/pytac.

Two pieces of software influenced its design:

* Matlab Middlelayer, used widely by accelerator physicists
* APHLA, high-level applications written in Python by the NSLS-II accelerator physics group


Software Overview
=================

Pytac provides a Python library ``pytac`` that makes it easier to communicate with machine hardware for online applications. Although it currently works with EPICS, the `cs.ControlSystem` class may be sub-classed to allow other control systems to be used.

The design is based around a ``Lattice`` object that contains a sequence of ``Element`` s.  Each element may have zero or more 'fields' (examples x, y, a1 or b2), associated with which are ``Device`` objects.  These devices contain the necessary information to request live data from the control system.

Data may be requested in ``ENG`` or ``PHYS`` units and will be converted as appropriate.  Two types of unit conversion are available: Polynomial (often used for linear conversion) and Piecewise Cubic Hermite Interpolating Polynomial (Pchip; often used for magnet data where field may not be linear with current).  In the case that measurement data (used to set up the conversion objects) is not in the same units as the physical models, further functions may be given to these objects to complete the conversion correctly.

Elements may be grouped into families (an element may be in more than one family) and requested from the lattice object in those families.

Machines are defined using a set of ``.csv`` files, located by default in the ``pytac/data`` directory.


Contents:
=========

.. toctree::
   :maxdepth: 4

   self
   examples
   pytac


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

