import mock
import pytest
import pytac
from pytac.element import Element
from pytac.lattice import Lattice
from pytac.data_source import DeviceDataSource
from pytac.units import PolyUnitConv

from constants import DUMMY_VALUE_1, DUMMY_VALUE_2, SP_PV, LATTICE_NAME


# Create mock devices and attach them to the element
x_device = mock.MagicMock()
x_device.name = 'x_device'
x_device.get_value.return_value = DUMMY_VALUE_1
y_device = mock.MagicMock()
y_device.name = 'y_device'
y_device.get_pv_name.return_value = SP_PV
# Add mock sim data_source
mock_sim_data_source = mock.MagicMock()
mock_sim_data_source.get_value.return_value = DUMMY_VALUE_2
mock_sim_data_source.units = pytac.PHYS


@pytest.fixture
def unit_uc():
    return PolyUnitConv([1, 0])


@pytest.fixture
def double_uc():
    return PolyUnitConv([2, 0])


@pytest.fixture
def simple_element(unit_uc):
    # A unit conversion object that returns the same as the input.
    element = Element('element1', 0, 'BPM', cell=1)
    element.add_to_family('family')
    element.set_data_source(DeviceDataSource(), pytac.LIVE)
    element.add_device('x', x_device, unit_uc)
    element.add_device('y', y_device, unit_uc)
    element.set_data_source(mock_sim_data_source, pytac.SIM)
    return element


@pytest.fixture
def simple_lattice(simple_element):
    lat = Lattice(LATTICE_NAME, 1)
    lat.add_element(simple_element)
    lat.set_data_source(DeviceDataSource(), pytac.LIVE)
    lat.add_device('x', x_device, unit_uc)
    lat.add_device('y', y_device, unit_uc)
    lat.set_data_source(mock_sim_data_source, pytac.SIM)
    return lat


@pytest.fixture(scope="session")
def vmx_ring():
    return pytac.load_csv.load('VMX', mock.MagicMock)


@pytest.fixture(scope="session")
def diad_ring():
    return pytac.load_csv.load('DIAD', mock.MagicMock)
