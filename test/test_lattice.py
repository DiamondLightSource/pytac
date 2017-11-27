import pytest
import pytac.lattice
import pytac.element
import pytac.device
import pytac.model
import mock
from pytac.units import PolyUnitConv

from constants import PREFIX, RB_SUFFIX, SP_SUFFIX, RB_PV, SP_PV, LATTICE


@pytest.fixture
def simple_element(identity=1):
    uc = PolyUnitConv([0, 1])

    # Create devices and attach them to the element
    element = pytac.element.Element(identity, 0, 'BPM', cell=1)
    device1 = pytac.device.Device(PREFIX, mock.MagicMock(), True, RB_SUFFIX, SP_SUFFIX)
    device2 = pytac.device.Device(PREFIX, mock.MagicMock(), True, RB_SUFFIX, SP_SUFFIX)
    element.add_to_family('family')

    element.set_model(pytac.model.DeviceModel(), pytac.LIVE)
    element.add_device('x', device1, uc)
    element.add_device('y', device2, uc)

    return element


@pytest.fixture
def simple_element_and_lattice(simple_element):
    l = pytac.lattice.Lattice(LATTICE, mock.MagicMock(), 1)
    l.add_element(simple_element)
    return simple_element, l


def test_create_lattice():
    l = pytac.lattice.Lattice(LATTICE, mock.MagicMock(), 1)
    assert(len(l)) == 0
    assert l.name == LATTICE


def test_get_devices(simple_element_and_lattice):
    _, lattice = simple_element_and_lattice
    devices = lattice.get_devices('family', 'x')
    assert len(devices) == 1
    assert devices[0].name == PREFIX


def test_get_devices_returns_empty_list_if_family_not_matched(simple_element_and_lattice):
    _, lattice = simple_element_and_lattice
    devices = lattice.get_devices('not-a-family', 'x')
    assert devices == []


def test_get_devices_returns_empty_list_if_field_not_matched(simple_element_and_lattice):
    _, lattice = simple_element_and_lattice
    devices = lattice.get_devices('family', 'not-a-field')
    assert devices == []


def test_get_device_names(simple_element_and_lattice):
    _, lattice = simple_element_and_lattice
    assert lattice.get_device_names('family', 'x') == [PREFIX]


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


def test_lattice_get_elements_by_cell(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    assert lattice.get_elements(cell=1) == [element]
    assert lattice.get_elements(cell=2) == []


def test_get_all_families(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    families = lattice.get_all_families()
    assert len(families) > 0


def test_get_pv_values(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    lattice.get_pv_values('family', 'x', pytac.RB)
    lattice._cs.get.assert_called_with([RB_PV])


def test_set_pv_values(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    lattice.set_pv_values('family', 'x', [1])
    lattice._cs.put.assert_called_with([SP_PV], [1])


def test_set_pv_values_raise_exception(simple_element_and_lattice):
    element, lattice = simple_element_and_lattice
    with pytest.raises(pytac.lattice.LatticeException):
        lattice.set_pv_values('family', 'x', [1, 2])


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
    l = pytac.lattice.Lattice(LATTICE, mock.MagicMock(), 1)
    element = pytac.element.Element(1, 1.0, 'Quad')
    with pytest.raises(pytac.lattice.LatticeException):
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
    lattice = pytac.lattice.Lattice(LATTICE, mock.MagicMock(), 1)
    assert lattice.get_energy() == 1
