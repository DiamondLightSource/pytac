import os
from pathlib import Path


PREFIX = "prefix"
RB_SUFFIX = ":rb"
SP_SUFFIX = ":sp"
RB_PV = PREFIX + RB_SUFFIX
SP_PV = PREFIX + SP_SUFFIX

DUMMY_VALUE_1 = 40.0
DUMMY_VALUE_2 = 4.7
DUMMY_VALUE_3 = -6

DUMMY_ARRAY = [DUMMY_VALUE_1]

LATTICE_NAME = "lattice"

CURRENT_DIR_PATH = Path(__file__).resolve().parent
