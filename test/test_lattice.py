import pytest
import pytac.lattice
import pytac.element
import pytac.device
import mock
from pytac.units import PolyUnitConv
from pytac.exceptions import ElementNotFoundException, PvException

DUMMY_NAME = 'dummy'


@pytest.fixture
def simple_element(identity=1):
    uc = PolyUnitConv([0, 1])

    # Create devices and attach them to the element
    element = pytac.element.Element(identity, 0, 'BPM')
    rb_pv = 'readback_pv'
    sp_pv = 'setpoint_pv'
    device1 = pytac.device.Device(mock.MagicMock(), True, sp_pv, rb_pv)
    device2 = pytac.device.Device(mock.MagicMock(), True, sp_pv, rb_pv)
    element.add_to_family('family')

    element.add_device('x', device1, uc)
    element.add_device('y', device2, uc)

    return element


@pytest.fixture
def simple_element_and_lattice(simple_element):
    l = pytac.lattice.Lattice(DUMMY_NAME, mock.MagicMock(), 1)
    l.add_element(simple_element)
    return simple_element, l


def test_create_lattice():
    l = pytac.lattice.Lattice(DUMMY_NAME, mock.MagicMock(), 1)
    assert(len(l)) == 0
    assert l.name == DUMMY_NAME


def test_non_negative_lattice():
    l = pytac.lattice.Lattice(DUMMY_NAME, mock.MagicMock(), 1)
    assert(len(l)) >= 0


def test_lattice_with_n_elements(simple_element_and_lattice):
    elem, lattice = simple_element_and_lattice

    # Getting elements
    lattice.add_element(elem)
    assert lattice[0] == elem
    assert lattice.get_elements() == [elem, elem]


def test_lattice_get_element_with_family(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    element.add_to_family('fam')
    assert lattice.get_elements('fam') == [element]
    assert lattice.get_elements('nofam') == []


def test_get_all_families(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    families = lattice.get_all_families()
    assert len(families) > 0


def test_get_family_values(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    lattice.get_family_values('family', 'x')
    lattice._cs.get.assert_called_with(['readback_pv'])


def test_set_family_values(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    lattice.set_family_values('family', 'x', [1])
    lattice._cs.put.assert_called_with(['readback_pv'], [1])


def test_set_family_values_raise_exception(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    with pytest.raises(PvException):
        lattice.set_family_values('family','x', [1, 2])


def test_s_position(simple_element_and_lattice):
    element1, lattice = simple_element_and_lattice
    assert lattice.get_s(element1) == 0.0

    element2 = pytac.element.Element(2, 1.0, 'Quad')
    lattice.add_element(element2)
    assert lattice.get_s(element2) == 0.0

    element3 = pytac.element.Element(3, 2.0, 'Quad')
    lattice.add_element(element3)
    assert lattice.get_s(element3) == 1.0

def test_get_s_throws_exception_if_element_not_in_lattice():
    l = pytac.lattice.Lattice(DUMMY_NAME, mock.MagicMock(), 1)
    element = pytac.element.Element(1, 1.0, 'Quad')
    with pytest.raises(ElementNotFoundException):
        l.get_s(element)

def test_get_family_s(simple_element_and_lattice):
    element1, lattice = simple_element_and_lattice
    assert lattice.get_family_s('family') == [0]

    element2 = pytac.element.Element(2, 1.0, 'family')
    element2.add_to_family('family')
    lattice.add_element(element2)
    assert lattice.get_family_s('family') == [0, 0]

    element3 = pytac.element.Element(3, 1.5, 'family')
    element3.add_to_family('family')
    lattice.add_element(element3)
    assert lattice.get_family_s('family') == [0, 0, 1.0]

    element4 = pytac.element.Element(3, 1.5, 'family')
    element4.add_to_family('family')
    lattice.add_element(element4)
    assert lattice.get_family_s('family') == [0, 0, 1.0, 2.5]

def test_lattice_initial_energy():
    lattice = pytac.lattice.Lattice(DUMMY_NAME, mock.MagicMock(), 1)
    assert lattice.get_energy() == 1
