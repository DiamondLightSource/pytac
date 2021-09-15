from unittest import mock

import numpy
import pytest

from constants import DUMMY_ARRAY, RB_PV, SP_PV
import pytac


def test_get_values_live(simple_epics_lattice, mock_cs):
    simple_epics_lattice.get_element_values("family", "x", pytac.RB, pytac.PHYS)
    mock_cs.get_multiple.assert_called_with([RB_PV], True)


def test_get_values_sim(simple_epics_lattice):
    mock_ds = mock.Mock(units=pytac.PHYS)
    mock_uc = mock.Mock()
    simple_epics_lattice[0].set_data_source(mock_ds, pytac.SIM)
    simple_epics_lattice[0].set_unitconv("a_field", mock_uc)
    simple_epics_lattice.get_element_values(
        "family", "a_field", pytac.RB, pytac.ENG, pytac.SIM
    )
    mock_ds.get_value.assert_called_with("a_field", pytac.RB, True)
    mock_uc.convert.assert_called_once()


def test_set_element_values_live(simple_epics_lattice, mock_cs):
    simple_epics_lattice.set_element_values("family", "x", [1], units=pytac.PHYS)
    mock_cs.set_multiple.assert_called_with([SP_PV], [1], True)


def test_set_element_values_sim(simple_epics_lattice):
    mock_ds = mock.Mock(units=pytac.PHYS)
    mock_uc = mock.Mock()
    mock_uc.convert.return_value = 1
    simple_epics_lattice[0].set_data_source(mock_ds, pytac.SIM)
    simple_epics_lattice[0].set_unitconv("a_field", mock_uc)
    simple_epics_lattice.set_element_values(
        "family", "a_field", [1], pytac.ENG, pytac.SIM
    )
    mock_ds.set_value.assert_called_with("a_field", 1, True)
    mock_uc.convert.assert_called_once_with(1, origin=pytac.ENG, target=pytac.PHYS)


def test_set_element_values_raises_correctly(simple_epics_lattice):
    with pytest.raises(IndexError):
        simple_epics_lattice.set_element_values("family", "x", [1, 2])
    with pytest.raises(IndexError):
        simple_epics_lattice.set_element_values(
            "family", "x", [1, 2], data_source=pytac.SIM
        )


@pytest.mark.parametrize(
    "dtype, expected",
    (
        (numpy.float64, numpy.array(DUMMY_ARRAY, dtype=numpy.float64)),
        (numpy.int32, numpy.array(DUMMY_ARRAY, dtype=numpy.int32)),
        (numpy.bool_, numpy.array(DUMMY_ARRAY, dtype=numpy.bool_)),
        (None, DUMMY_ARRAY),
    ),
)
def test_get_values_returns_numpy_array_if_requested(
    simple_epics_lattice, dtype, expected, mock_cs
):
    values = simple_epics_lattice.get_element_values(
        "family", "x", pytac.RB, dtype=dtype
    )
    numpy.testing.assert_equal(values, expected)
    mock_cs.get_multiple.assert_called_with([RB_PV], True)


@pytest.mark.parametrize("pv_type", ["readback", "setpoint"])
def test_get_element_pv_name(pv_type, simple_epics_element):
    assert isinstance(simple_epics_element.get_pv_name("x", pv_type), str)
    assert isinstance(simple_epics_element.get_pv_name("y", pv_type), str)
    with pytest.raises(pytac.exceptions.FieldException):
        simple_epics_element.get_pv_name("not_a_field", pv_type)


@pytest.mark.parametrize("pv_type", ["readback", "setpoint"])
def test_get_lattice_pv_name(pv_type, simple_epics_lattice):
    assert isinstance(simple_epics_lattice.get_pv_name("x", pv_type), str)
    assert isinstance(simple_epics_lattice.get_pv_name("y", pv_type), str)
    with pytest.raises(pytac.exceptions.FieldException):
        simple_epics_lattice.get_pv_name("not_a_field", pv_type)


def test_get_value_uses_cs_if_data_source_live(simple_epics_element, mock_cs):
    simple_epics_element.get_value("x", handle=pytac.SP, data_source=pytac.LIVE)
    mock_cs.get_single.assert_called_with(SP_PV, True)
    simple_epics_element.get_value("x", handle=pytac.RB, data_source=pytac.LIVE)
    mock_cs.get_single.assert_called_with(RB_PV, True)


def test_get_value_raises_HandleExceptions(simple_epics_element):
    with pytest.raises(pytac.exceptions.HandleException):
        simple_epics_element.get_value("y", "unknown_handle")


def test_lattice_get_pv_name_raises_DataSourceException(simple_epics_lattice):
    basic_epics_lattice = simple_epics_lattice
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_epics_lattice.get_pv_name("basic", pytac.RB)
    del basic_epics_lattice._data_source_manager._data_sources[pytac.LIVE]
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_epics_lattice.get_pv_name("x", pytac.RB)


def test_set_element_values_length_mismatch_raises_IndexError(simple_epics_lattice):
    with pytest.raises(IndexError):
        simple_epics_lattice.set_element_values("family", "x", [1, 2])
    with pytest.raises(IndexError):
        simple_epics_lattice.set_element_values("family", "x", [])


def test_element_get_pv_name_raises_exceptions(simple_epics_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_epics_element.get_pv_name("unknown_field", "setpoint")
    basic_epics_element = simple_epics_element
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_epics_element.get_pv_name("basic", pytac.RB)
    del basic_epics_element._data_source_manager._data_sources[pytac.LIVE]
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_epics_element.get_pv_name("x", pytac.RB)


def test_create_EpicsDevice_raises_DataSourceException_if_no_PVs_are_given():
    with pytest.raises(pytac.exceptions.DataSourceException):
        pytac.device.EpicsDevice("device_1", "a_control_system")
