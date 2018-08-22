import copy
import mock
import numpy
import pytest
import pytac
from pytac.epics import EpicsElement, EpicsLattice
from pytac.model import DeviceModel
from pytac.units import PolyUnitConv
from constants import RB_PV, SP_PV


DUMMY_ARRAY = [1]


@pytest.fixture
def mock_cs():
    cs = mock.MagicMock()
    cs.get.return_value = DUMMY_ARRAY
    return cs


@pytest.fixture
def mock_device():

    def get_pv_name(handle):
        return SP_PV if handle == pytac.SP else RB_PV

    device = mock.MagicMock()
    device.get_value.return_value = 1
    device.get_pv_name.side_effect = get_pv_name
    return device


@pytest.fixture
def simple_epics_element(mock_device):
    uc = PolyUnitConv([0, 1])
    element = EpicsElement(1, 0, 'BPM', cell=1)
    x_device = mock_device
    x_device.name = 'x_device'
    print(x_device.get_pv_name)
    y_device = copy.copy(x_device)
    y_device.name = 'y_device'
    element.add_to_family('family')

    element.set_model(DeviceModel(), pytac.LIVE)
    element.add_device('x', x_device, uc)
    element.add_device('y', y_device, uc)

    return element


@pytest.fixture
def simple_epics_lattice(simple_epics_element, mock_cs):
    lat = EpicsLattice('lattice', 1, mock_cs)
    lat.add_element(simple_epics_element)
    return lat


def test_get_values(simple_epics_lattice):
    simple_epics_lattice.get_values('family', 'x', pytac.RB)
    simple_epics_lattice._cs.get.assert_called_with([RB_PV])


def test_set_values(simple_epics_lattice):
    simple_epics_lattice.set_values('family', 'x', [1])
    simple_epics_lattice._cs.put.assert_called_with([SP_PV], [1])


@pytest.mark.parametrize(
    'dtype,expected', (
        (numpy.float64, numpy.array(DUMMY_ARRAY, dtype=numpy.float64)),
        (numpy.int32, numpy.array(DUMMY_ARRAY, dtype=numpy.int32)),
        (numpy.bool_, numpy.array(DUMMY_ARRAY, dtype=numpy.bool_)),
        (None, DUMMY_ARRAY)
    ))
def test_get_values_returns_numpy_array_if_requested(simple_epics_lattice, dtype, expected):
    values = simple_epics_lattice.get_values('family', 'x', pytac.RB, dtype=dtype)
    numpy.testing.assert_equal(values, expected)
    simple_epics_lattice._cs.get.assert_called_with([RB_PV])
