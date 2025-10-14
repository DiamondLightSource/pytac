from unittest import mock

import pytest

import pytac
from constants import DUMMY_VALUE_1, DUMMY_VALUE_2
from pytac.device import SimpleDevice
from pytac.element import Element
from pytac.lattice import Lattice


def test_create_element():
    lat = Lattice("")
    e = Element(6.0, "BPM", "bpm1", lat)
    assert e.length == 6.0
    assert e.type_ == "BPM"
    assert e.name == "bpm1"
    assert e._lattice == lat


def test_element_properties_are_none_without_lattice():
    e = Element(1.2, "SEXT")
    assert e.index is None
    assert e.s is None
    assert e.cell is None
    lat = mock.Mock()
    lat.cell_length = None
    e._lattice = lat
    assert e.cell is None


def test_element_properties_with_lattice():
    e1 = Element(3.1, "DRFIT", "d1")
    e2 = Element(1.3, "DRFIT", "d2")
    lat = Lattice("", symmetry=2)
    lat.add_element(e1)
    lat.add_element(e2)
    assert e1.index == 1
    assert e2.index == 2
    assert e1.s == 0.0
    assert e2.s == 3.1
    assert e1.cell == 1
    assert e2.cell == 2


def test_add_element_to_family_and_case_insensitive_retrieval():
    e = Element(6.0, "QUAD", "dummy")
    e.add_to_family("FAM")
    # Lowercase only
    assert "fam" in e.families
    assert "FAM" not in e.families
    assert e.is_in_family("fam")
    assert e.is_in_family("FAM")


def test_device_methods_raise_data_source_exception_if_no_live_data_source(
    simple_element,
):
    basic_element = simple_element
    del basic_element._data_source_manager._data_sources[pytac.LIVE]
    d = SimpleDevice(0)
    uc = pytac.units.NullUnitConv()
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_element.add_device("x", d, uc)
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_element.get_device("x")


def test_get_device_raises_key_error_if_device_not_present(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.get_device("not-a-device")


def test_get_unitconv_returns_unitconv_object(simple_element, unit_uc, double_uc):
    assert simple_element.get_unitconv("x") == unit_uc
    assert simple_element.get_unitconv("y") == double_uc


def test_set_unitconv(simple_element):
    with pytest.raises(KeyError):
        simple_element._data_source_manager._uc["field1"]
    uc = mock.Mock()
    simple_element.set_unitconv("field1", uc)
    assert simple_element._data_source_manager._uc["field1"] == uc


def test_get_unitconv_raises_field_exception_if_device_not_present(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.get_unitconv("not-a-device")


def test_get_value_uses_uc_if_necessary_for_cs_call(simple_element, double_uc):
    simple_element._data_source_manager._uc["x"] = double_uc
    assert simple_element.get_value(
        "x", handle=pytac.SP, units=pytac.PHYS, data_source=pytac.LIVE
    ) == (DUMMY_VALUE_1 * 2)


def test_get_value_uses_uc_if_necessary_for_sim_call(simple_element, double_uc):
    simple_element._data_source_manager._uc["x"] = double_uc
    assert simple_element.get_value(
        "x", handle=pytac.SP, units=pytac.ENG, data_source=pytac.SIM
    ) == (DUMMY_VALUE_2 / 2)
    simple_element._data_source_manager._data_sources[
        pytac.SIM
    ].get_value.assert_called_with("x", pytac.SP, True)


def test_set_value_eng(simple_element):
    simple_element.set_value("x", DUMMY_VALUE_2)
    # No conversion needed
    simple_element.get_device("x").set_value.assert_called_with(DUMMY_VALUE_2, True)


def test_set_value_phys(simple_element, double_uc):
    simple_element._data_source_manager._uc["x"] = double_uc
    simple_element.set_value("x", DUMMY_VALUE_2, units=pytac.PHYS)
    # Conversion fron physics to engineering units
    simple_element.get_device("x").set_value.assert_called_with(DUMMY_VALUE_2 / 2, True)


def test_set_exceptions(simple_element, unit_uc):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.set_value("unknown_field", 40.0)
    with pytest.raises(pytac.exceptions.DataSourceException):
        simple_element.set_value("y", 40.0, data_source="unknown_data_source")
    simple_element._data_source_manager._uc["uc_but_no_data_source"] = unit_uc
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.set_value("uc_but_no_data_source", 40.0)


def test_get_exceptions(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.get_value("unknown_field", "setpoint")
    with pytest.raises(pytac.exceptions.DataSourceException):
        simple_element.get_value("y", "setpoint", data_source="unknown_data_source")


def test_identity_conversion(simple_element):
    value_physics = simple_element.get_value("x", "setpoint", pytac.PHYS)
    value_machine = simple_element.get_value("x", "setpoint", pytac.ENG)
    assert value_machine == DUMMY_VALUE_1
    assert value_physics == DUMMY_VALUE_1


def test_get_fields(simple_element):
    assert set(simple_element.get_fields()[pytac.LIVE]) == {"y", "x"}


def test_element_representation():
    elem = Element(0.1, "BPM")
    assert str(elem) == "<Element length 0.1 m, families >"
    elem.add_to_family("fam1")
    assert str(elem) == "<Element length 0.1 m, families fam1>"
    elem.name = "bpm1"
    assert str(elem) == "<Element 'bpm1', length 0.1 m, families fam1>"
    lat = Lattice("")
    lat.add_element(elem)
    assert str(elem) == ("<Element 'bpm1', index 1, length 0.1 m, families fam1>")
    lat.symmetry = 2
    assert str(elem) == (
        "<Element 'bpm1', index 1, length 0.1 m, cell 1, families fam1>"
    )
    elem.name = None
    assert str(elem) == ("<Element index 1, length 0.1 m, cell 1, families fam1>")


def test_set_lattice_reference():
    elem1 = Element(1.0, "BPM")
    lat1 = Lattice("one")
    elem2 = Element(2.0, "BPM", lattice=lat1)
    lat2 = Lattice("two")
    assert elem1._lattice is None
    assert elem2._lattice == lat1
    elem1.set_lattice(lat1)
    elem2.set_lattice(lat2)
    assert elem1._lattice == lat1
    assert elem2._lattice == lat2
