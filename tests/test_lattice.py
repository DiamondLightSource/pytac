from unittest import mock

import numpy
import pytest

import pytac
from constants import DUMMY_ARRAY, LATTICE_NAME
from pytac.element import Element
from pytac.lattice import Lattice


def test_create_lattice():
    lat = Lattice(LATTICE_NAME)
    assert (len(lat)) == 0
    assert lat.name == LATTICE_NAME


def test_add_element_to_lattice():
    lat1 = Lattice("lat1")
    elem = Element(0.5, "DRIFT")
    assert lat1._elements == []
    assert elem._lattice is None
    lat1.add_element(elem)
    assert lat1._elements == [elem]
    assert elem._lattice == lat1
    lat2 = Lattice("lat2")
    lat2.add_element(elem)
    assert elem._lattice == lat2


def test_lattice_without_symmetry():
    lat = Lattice("")
    assert lat.cell_length is None
    assert lat.cell_bounds is None
    lat = Lattice("", 6)
    assert lat.cell_length is None
    assert lat.cell_bounds is None


def test_lattice_cell_properties():
    lat = Lattice("", 2)
    for i in range(5):
        lat.add_element(Element(0.5, "DRIFT"))
    assert lat.cell_length == 1.25
    assert lat.cell_bounds == [1, 4, 5]


def test_get_element_devices(simple_lattice):
    devices = simple_lattice.get_element_devices("family", "x")
    assert len(devices) == 1
    assert devices[0].name == "x_device"


def test_device_methods_raise_DataSourceException_if_no_live_data_source(
    simple_lattice,
):
    basic_lattice = simple_lattice
    del basic_lattice._data_source_manager._data_sources[pytac.LIVE]
    d = pytac.device.SimpleDevice(0)
    uc = pytac.units.NullUnitConv()
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_lattice.add_device("x", d, uc)
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_lattice.get_device("x")


def test_get_unitconv_raises_FieldException_if_no_uc_for_field(simple_lattice):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_lattice.get_unitconv("not_a_field")


def test_get_and_set_unitconv():
    lat = Lattice("")
    with pytest.raises(KeyError):
        lat._data_source_manager._uc["field1"]
    uc = mock.Mock()
    lat.set_unitconv("field1", uc)
    assert lat._data_source_manager._uc["field1"] == uc
    assert lat.get_unitconv("field1") == uc


def test_get_value_raises_exceptions_correctly(simple_lattice):
    with pytest.raises(pytac.exceptions.DataSourceException):
        simple_lattice.get_value("x", data_source="not_a_data_source")
    with pytest.raises(pytac.exceptions.FieldException):
        simple_lattice.get_value("not_a_field")


def test_set_value_raises_exceptions_correctly(simple_lattice):
    with pytest.raises(pytac.exceptions.DataSourceException):
        simple_lattice.set_value("x", 0, data_source="not_a_data_source")
    with pytest.raises(pytac.exceptions.FieldException):
        simple_lattice.set_value("not_a_field", 0)


def test_get_element_devices_raises_ValueError_for_mismatched_family(simple_lattice):
    with pytest.raises(ValueError):
        devices = simple_lattice.get_element_devices("not-a-family", "x")
    basic_element = simple_lattice.get_elements("family")[0]
    basic_lattice = Lattice("basic_lattice")
    del basic_element._data_source_manager._data_sources[pytac.LIVE]
    basic_lattice.add_element(basic_element)
    devices = basic_lattice.get_element_devices("family", "x")
    assert devices == []


def test_get_element_devices_raises_FieldException_if_field_not_matched(simple_lattice):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_lattice.get_element_devices("family", "not-a-field")


def test_get_element_device_names(simple_lattice):
    assert simple_lattice.get_element_device_names("family", "x") == ["x_device"]


def test_lattice_get_elements_with_n_elements(simple_lattice):
    elem = simple_lattice[0]
    simple_lattice.add_element(elem)
    assert simple_lattice[1] == elem
    assert simple_lattice.get_elements() == [elem, elem]
    simple_lattice._elements = []
    assert len(simple_lattice) == 0
    with pytest.raises(ValueError):
        simple_lattice.get_elements()


def test_lattice_get_elements_with_family(simple_lattice):
    elem = simple_lattice[0]
    elem.add_to_family("fam")
    assert simple_lattice.get_elements("fam") == [elem]
    with pytest.raises(ValueError):
        simple_lattice.get_elements("nofam")


def test_lattice_get_elements_by_cell(simple_lattice):
    elem = simple_lattice[0]
    elem.length = 0.1  # length hacking as cells require a non-zero...
    assert simple_lattice.get_elements(cell=1) == [elem]
    elem.length = 0.0  # ...length lattice to work.
    with pytest.raises(ValueError):
        simple_lattice.get_elements(cell=2)


def test_get_all_families(simple_lattice):
    families = simple_lattice.get_all_families()
    assert list(families) == ["family"]


def test_get_element_values(simple_lattice):
    simple_lattice.get_element_values("family", "x", pytac.RB)
    simple_lattice.get_element_devices("family", "x")[0].get_value.assert_called_with(
        pytac.RB, True
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
def test_get_element_values_returns_numpy_array_if_requested(
    simple_lattice, dtype, expected
):
    values = simple_lattice.get_element_values("family", "x", pytac.RB, dtype=dtype)
    numpy.testing.assert_equal(values, expected)


def test_set_element_values(simple_lattice):
    simple_lattice.set_element_values("family", "x", [1])
    simple_lattice.get_element_devices("family", "x")[0].set_value.assert_called_with(
        1, True
    )


def test_set_element_values_raises_Exceptions_correctly(simple_lattice):
    with pytest.raises(IndexError):
        simple_lattice.set_element_values("family", "x", [1, 2])
    with pytest.raises(IndexError):
        simple_lattice.set_element_values("family", "x", [])


def test_get_family_s(simple_lattice):
    assert simple_lattice.get_family_s("family") == [0]

    element2 = Element(1.0, "family")
    element2.add_to_family("family")
    simple_lattice.add_element(element2)
    assert simple_lattice.get_family_s("family") == [0, 0]

    element3 = Element(2.5, "family")
    element3.add_to_family("family")
    simple_lattice.add_element(element3)
    assert simple_lattice.get_family_s("family") == [0, 0, 1.0]

    element4 = Element(0.0, "family")
    element4.add_to_family("family")
    simple_lattice.add_element(element4)
    assert simple_lattice.get_family_s("family") == [0, 0, 1.0, 3.5]


def test_get_default_arguments(simple_lattice):
    assert simple_lattice.get_default_units() == pytac.ENG
    assert simple_lattice.get_default_data_source() == pytac.LIVE


def test_set_default_arguments(simple_lattice):
    simple_lattice.set_default_units(pytac.PHYS)
    simple_lattice.set_default_data_source(pytac.SIM)
    assert simple_lattice._data_source_manager.default_units == pytac.PHYS
    assert simple_lattice._data_source_manager.default_data_source == pytac.SIM


def test_set_default_arguments_exceptions(simple_lattice):
    with pytest.raises(pytac.exceptions.UnitsException):
        simple_lattice.set_default_units("invalid_units")
    with pytest.raises(pytac.exceptions.DataSourceException):
        simple_lattice.set_default_data_source("invalid_data_source")


def test_convert_family_values(simple_lattice):
    post_values = simple_lattice.convert_family_values(
        "family", "y", [12], pytac.PHYS, pytac.ENG
    )
    assert post_values == [6]
    post_values = simple_lattice.convert_family_values(
        "family", "y", [12], pytac.ENG, pytac.PHYS
    )
    assert post_values == [24]
    post_values = simple_lattice.convert_family_values(
        "family", "y", [12], pytac.ENG, pytac.ENG
    )
    assert post_values == [12]
    post_values = simple_lattice.convert_family_values(
        "family", "y", [12], pytac.PHYS, pytac.PHYS
    )
    assert post_values == [12]


def test_convert_family_values_length_mismatch_raises_IndexError(simple_lattice):
    with pytest.raises(IndexError):
        simple_lattice.convert_family_values(
            "family", "x", [1, 2], pytac.ENG, pytac.PHYS
        )
    with pytest.raises(IndexError):
        simple_lattice.convert_family_values("family", "x", [], pytac.ENG, pytac.PHYS)
