.. docs documentation master file, created by
   sphinx-quickstart on Mon May  8 13:02:08 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.  include:: intro.rst

Python Toolkit for Accelerator Controls
=======================================
Python Toolkit for Accelerator Controls (Pytac) is a Python library intended to make it easy to work with particle accelerators.

It is a framework that implements high level configure/run behaviour of control system components.  Pytac  includes a set of API (Application Programming Interface) which is used for writing further scripts and interactive controls. The function of Pytac is to provide a scripting language for on-line control.



Software Overview
=================
Pytac provides a library of software that communicates with machine hardware for online applications. It is important to note that although the online get/set routines originally communicated via EPICS Channel Access they can now communicate with a variety of control systems. There are only two core functions that need to be re-programmed to work with the new control system - get and put inside the ControlSystem class.



Contents:
=========

.. toctree::
   :maxdepth: 4

   intro
   examples
   pytac


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

