import sys

if sys.version_info[1] <= 7:
    from importlib_metadata import version  # noqa
else:
    from importlib.metadata import version  # noqa

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

from . import (  # isort:skip
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

__version__ = version("pytac")
del version

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
