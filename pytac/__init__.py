"""Pytac: Python Toolkit for Accelerator Controls."""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

__version__ = version("pytac")


# PV types.
SP = "setpoint"
RB = "readback"
# Unit systems.
ENG = "engineering"
PHYS = "physics"
# Data Source types.
SIM = "simulation"
LIVE = "live"
# Default argument flag.
DEFAULT = "default"


from . import (  # noqa: 402
    data_source,
    device,
    element,
    exceptions,
    lattice,
    load_csv,
    units,
    utils,
)

"""Error 402 is suppressed as we cannot import these modules at the top of the
file as the strings above must be set first or the imports will fail.
"""
__all__ = [
    "data_source",
    "device",
    "element",
    "exceptions",
    "lattice",
    "load_csv",
    "units",
    "utils",
]
