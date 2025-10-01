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

# Update this to the lattice mode you want to be used in *most* tests.
TESTING_MODE = "I04"
TESTING_MODE_RING = "I04".lower() + "_ring"

# Update this with the ringmodes that pytac supports
SUPPORTED_MODES = {
        "I04",
        "DIAD",
        "DIADSP",
        "DIADTHz",
        "I04SP",
        "I04THz",
        "48",
    }