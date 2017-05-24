.. docs documentation master file, created by
   sphinx-quickstart on Mon May  8 13:02:08 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.  include:: intro.rst

Welcome to PYTAC's documentation!
=================================
PYTAC is a python library for accelerator commissioning and beam study.

It is a framework that implements high level configure/run behaviour of control system components.PYTAC includes a set of API (Application Programming Interface) which is used for writing further scripts and interactive controls. The function of Python Middle Layer is to provide a scripting language for on-line control, including non-EPICS based control systems.



Software Overview
=================
Python Toolkit for Accelerator Controls (PYTAC) provides a library of software that communicates with machine hardware for online applications. It is important to note that although the online get/set routines originally communicated via EPICS Channel Access they can now communicate with a variety of control systems. There are only two core functions that need to be re-programmed to work with the new control system - get and put inside the ControlSystem class.



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

