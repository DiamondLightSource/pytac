from pathlib import Path
from unittest.mock import patch

import pytest
from testfixtures import LogCapture

import pytac
from constants import SUPPORTED_MODES, TESTING_MODE
from pytac.load_csv import available_ringmodes, load, load_unitconv, resolve_unitconv


@pytest.fixture
def mock_cs_raises_ImportError():
    """We create a mock control system to replace CothreadControlSystem, so
        that we can check that when it raises an ImportError load_csv.load
        catches it and raises a ControlSystemException instead.
    N.B. Our new CothreadControlSystem is nested inside a fixture so it can be
     patched into pytac.cothread_cs to replace the existing
     CothreadControlSystem class. The new CothreadControlSystem created here is
     a function not a class (like the original) to prevent it from raising the
     ImportError when the code is compiled.
    """

    def CothreadControlSystem():
        raise ImportError

    return CothreadControlSystem


def test_default_control_system_import():
    """In this test we:
    - assert that the lattice is indeed loaded if no execeptions are raised
    - assert that the default control system is indeed cothread and that it
       is loaded onto the lattice correctly
    """
    assert bool(load(TESTING_MODE))
    assert isinstance(load(TESTING_MODE)._cs, pytac.cothread_cs.CothreadControlSystem)


def test_import_fail_raises_ControlSystemException(mock_cs_raises_ImportError):
    """In this test we:
    - check that load corectly fails if cothread cannot be imported
    - check that when the import of the CothreadControlSystem fails the
       ImportError raised is replaced with a ControlSystemException
    """
    with patch("pytac.cothread_cs.CothreadControlSystem", mock_cs_raises_ImportError):
        with pytest.raises(pytac.exceptions.ControlSystemException):
            load(TESTING_MODE)


def test_elements_loaded(lattice):
    assert len(lattice) == 4
    assert len(lattice.get_elements("drift")) == 2
    assert lattice.get_length() == 2.6


def test_element_details_loaded(lattice):
    quad = lattice.get_elements("quad")[0]
    assert quad.cell == 1
    assert quad.s == 1.0
    assert quad.index == 2


def test_devices_loaded(lattice):
    quads = lattice.get_elements("quad")
    assert len(quads) == 1
    assert quads[0].get_pv_name(field="b1", handle=pytac.RB) == "Q1:RB"
    assert quads[0].get_pv_name(field="b1", handle=pytac.SP) == "Q1:SP"


def test_families_loaded(lattice):
    assert lattice.get_all_families() == set(
        ["drift", "sext", "quad", "ds", "qf", "qs", "sd"]
    )
    assert lattice.get_elements("quad")[0].families == set(["quad", "qf", "qs"])


def test_load_unitconv_warns_if_pchip_or_poly_data_file_not_found(
    lattice, mode_dir, polyconv_file, pchipconv_file
):
    with LogCapture() as log:
        load_unitconv(mode_dir, lattice)
    log.check(
        (
            "root",
            "WARNING",
            f"{polyconv_file} not found, unable to load PolyUnitConvs.",
        ),
        (
            "root",
            "WARNING",
            f"{pchipconv_file} not found, unable to load PchipUnitConvs.",
        ),
    )


def test_resolve_unitconv_raises_UnitsException_if_pchip_or_poly_data_file_not_found(
    polyconv_file, pchipconv_file
):
    uc_params = {
        "uc_type": "poly",
        "uc_id": 1,
        "phys_units": "m^-2",
        "eng_units": "A",
        "lower_lim": 0,
        "upper_lim": 200,
    }
    with pytest.raises(pytac.exceptions.UnitsException):
        resolve_unitconv(uc_params, {}, polyconv_file, pchipconv_file)
    uc_params = {
        "uc_type": "pchip",
        "uc_id": 2,
        "phys_units": "m^-3",
        "eng_units": "A",
        "lower_lim": -100,
        "upper_lim": 100,
    }
    with pytest.raises(pytac.exceptions.UnitsException):
        resolve_unitconv(uc_params, {}, polyconv_file, pchipconv_file)


def test_resolve_unitconv_raises_UnitsException_if_unrecognised_UnitConv_type(
    polyconv_file, pchipconv_file
):
    uc_params = {
        "uc_type": "unrecognised",
        "uc_id": 0,
        "phys_units": "",
        "eng_units": "",
        "lower_lim": 0,
        "upper_lim": 0,
    }
    with pytest.raises(pytac.exceptions.UnitsException):
        resolve_unitconv(uc_params, {}, polyconv_file, pchipconv_file)


def test_available_ringmodes():
    assert available_ringmodes() == SUPPORTED_MODES
    bad_path = Path(__file__).resolve().parent.parent
    with pytest.raises(OSError):
        available_ringmodes(bad_path)
    good_path = bad_path / "src/pytac/data"
    assert available_ringmodes(good_path) == SUPPORTED_MODES
