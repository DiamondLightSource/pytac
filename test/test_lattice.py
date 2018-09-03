import numpy
import pytest
import pytac
from pytac.element import Element
from pytac.lattice import Lattice
from constants import DUMMY_ARRAY, LATTICE_NAME


def test_create_lattice():
    lat = Lattice(LATTICE_NAME, 1)
    assert(len(lat)) == 0
    assert lat.get_energy() == 1
    assert lat.name == LATTICE_NAME


def test_get_element_devices(simple_lattice):
    devices = simple_lattice.get_element_devices('family', 'x')
    assert len(devices) == 1
    assert devices[0].name == 'x_device'


def test_get_element_devices_returns_empty_list_if_family_not_matched(simple_lattice):
    devices = simple_lattice.get_element_devices('not-a-family', 'x')
    assert devices == []


def test_get_element_devices_returns_empty_list_if_field_not_matched(simple_lattice):
    devices = simple_lattice.get_element_devices('family', 'not-a-field')
    assert devices == []


def test_get_element_device_names(simple_lattice):
    assert simple_lattice.get_element_device_names('family',
                                                   'x') == ['x_device']


def test_lattice_with_n_elements(simple_lattice):
    elem = simple_lattice[0]
    simple_lattice.add_element(elem)
    assert simple_lattice[1] == elem
    assert simple_lattice.get_elements() == [elem, elem]


def test_lattice_get_element_with_family(simple_lattice):
    elem = simple_lattice[0]
    elem.add_to_family('fam')
    assert simple_lattice.get_elements('fam') == [elem]
    assert simple_lattice.get_elements('nofam') == []


def test_lattice_get_elements_by_cell(simple_lattice):
    elem = simple_lattice[0]
    assert simple_lattice.get_elements(cell=1) == [elem]
    assert simple_lattice.get_elements(cell=2) == []


def test_get_all_families(simple_lattice):
    families = simple_lattice.get_all_families()
    assert list(families) == ['family']


def test_get_element_values(simple_lattice):
    simple_lattice.get_element_values('family', 'x', pytac.RB)
    simple_lattice.get_element_devices('family', 'x')[0].get_value.assert_called_with(pytac.RB)


@pytest.mark.parametrize('dtype, expected',
                         ((numpy.float64, numpy.array(DUMMY_ARRAY,
                                                      dtype=numpy.float64)),
                          (numpy.int32, numpy.array(DUMMY_ARRAY,
                                                    dtype=numpy.int32)),
                          (numpy.bool_, numpy.array(DUMMY_ARRAY,
                                                    dtype=numpy.bool_)),
                          (None, DUMMY_ARRAY)))
def test_get_element_values_returns_numpy_array_if_requested(simple_lattice,
                                                             dtype, expected):
    values = simple_lattice.get_element_values('family', 'x', pytac.RB,
                                               dtype=dtype)
    numpy.testing.assert_equal(values, expected)


def test_set_element_values(simple_lattice):
    simple_lattice.set_element_values('family', 'x', [1])
    simple_lattice.get_element_devices('family',
                                       'x')[0].set_value.assert_called_with(1)


def test_set_element_values_raise_exception_if_number_of_values_does_not_match(simple_lattice):
    with pytest.raises(pytac.exceptions.LatticeException):
        simple_lattice.set_element_values('family', 'x', [1, 2])


def test_s_position(simple_lattice):
    element1 = simple_lattice[0]
    assert simple_lattice.get_s(element1) == 0.0

    element2 = Element(2, 1.0, 'Quad')
    simple_lattice.add_element(element2)
    assert simple_lattice.get_s(element2) == 0.0

    element3 = Element(3, 2.0, 'Quad')
    simple_lattice.add_element(element3)
    assert simple_lattice.get_s(element3) == 1.0


def test_get_s_throws_exception_if_element_not_in_lattice():
    lat = Lattice(LATTICE_NAME, 1)
    element = Element(1, 1.0, 'Quad')
    with pytest.raises(pytac.exceptions.LatticeException):
        lat.get_s(element)


def test_get_family_s(simple_lattice):
    assert simple_lattice.get_family_s('family') == [0]

    element2 = Element(2, 1.0, 'family')
    element2.add_to_family('family')
    simple_lattice.add_element(element2)
    assert simple_lattice.get_family_s('family') == [0, 0]

    element3 = Element(3, 1.5, 'family')
    element3.add_to_family('family')
    simple_lattice.add_element(element3)
    assert simple_lattice.get_family_s('family') == [0, 0, 1.0]

    element4 = Element(3, 1.5, 'family')
    element4.add_to_family('family')
    simple_lattice.add_element(element4)
    assert simple_lattice.get_family_s('family') == [0, 0, 1.0, 2.5]
