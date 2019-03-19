"""Pytac: Python Toolkit for Accelerator Controls."""
# PV types.
SP = 'setpoint'
RB = 'readback'
# Unit systems.
ENG = 'engineering'
PHYS = 'physics'
# Data Source types.
SIM = 'simulation'
LIVE = 'live'
# Default argument flag.
DEFAULT = 'default'


from . import (data_source, device, element, exceptions, lattice, load_csv,
               units, utils)  # noqa: E402
"""Error 402 is suppressed as we cannot import these modules at the top of the
file as the strings above must be set first or the imports will fail.
"""
__all__ = ["data_source", "device", "element", "exceptions", "lattice",
           "load_csv", "units", "utils"]
