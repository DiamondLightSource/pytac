"""Top level API.

.. data:: __version__
    :type: str
"""

from ._version import __version__

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

from . import (
    data_source,
    device,
    element,
    exceptions,
    lattice,
    load_csv,
    units,
    utils,
)

__all__ = [
    "__version__",
    "data_source",
    "device",
    "element",
    "exceptions",
    "lattice",
    "load_csv",
    "units",
    "utils",
]
