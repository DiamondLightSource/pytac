import mock
import numpy
import pytest
import pytac
from pytac.epics import EpicsDevice, EpicsElement, EpicsLattice
from pytac.model import DeviceModel
from constants import DUMMY_ARRAY, RB_PV, SP_PV


@pytest.fixture
def mock_cs():
    cs = mock.MagicMock()
    cs.get.return_value = DUMMY_ARRAY
    return cs


@pytest.fixture
def simple_epics_element(mock_cs, unit_uc):
    element = EpicsElement(1, 0, 'BPM', cell=1)
    x_device = EpicsDevice('x_device', mock_cs, True, RB_PV, SP_PV)
    y_device = EpicsDevice('y_device', mock_cs, True, SP_PV, RB_PV)
    element.add_to_family('family')
    element.set_model(DeviceModel(), pytac.LIVE)
    element.add_device('x', x_device, unit_uc)
    element.add_device('y', y_device, unit_uc)
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


@pytest.mark.parametrize('pv_type', ['readback', 'setpoint'])
def test_get_pv_name(pv_type, simple_epics_element):
    assert isinstance(simple_epics_element.get_pv_name('x', pv_type), str)
    assert isinstance(simple_epics_element.get_pv_name('y', pv_type), str)


def test_get_value_uses_cs_if_model_live(simple_epics_element):
    simple_epics_element.get_value('x', handle=pytac.SP, model=pytac.LIVE)
    simple_epics_element.get_device('x')._cs.get.assert_called_with(SP_PV)
    simple_epics_element.get_value('x', handle=pytac.RB, model=pytac.LIVE)
    simple_epics_element.get_device('x')._cs.get.assert_called_with(RB_PV)


def test_get_value_raises_HandleExceptions(simple_epics_element):
    with pytest.raises(pytac.exceptions.HandleException):
        simple_epics_element.get_value('y', 'unknown_handle')
