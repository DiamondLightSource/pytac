import os
import mock
import pytest
import pytac
from pytac import load_csv
from pytac.element import Element
from pytac.lattice import Lattice
from pytac.data_source import DataSourceManager, DeviceDataSource
from pytac.units import PolyUnitConv
from pytac.epics import EpicsLattice, EpicsElement, EpicsDevice
from constants import DUMMY_VALUE_1, DUMMY_VALUE_2, RB_PV, SP_PV, LATTICE_NAME, CURRENT_DIR, DUMMY_ARRAY


# Create mock devices and attach them to the element
@pytest.fixture
def x_device():
    x_device = mock.MagicMock()
    x_device.name = 'x_device'
    x_device.get_value.return_value = DUMMY_VALUE_1
    return x_device


@pytest.fixture
def y_device():
    y_device = mock.MagicMock()
    y_device.name = 'y_device'
    y_device.get_pv_name.return_value = SP_PV
    return y_device


# Add mock sim data_source
@pytest.fixture
def mock_sim_data_source():
    mock_sim_data_source = mock.MagicMock()
    mock_sim_data_source.get_value.return_value = DUMMY_VALUE_2
    mock_sim_data_source.units = pytac.PHYS
    return mock_sim_data_source


@pytest.fixture
def unit_uc():
    return PolyUnitConv([1, 0])


@pytest.fixture
def double_uc():
    return PolyUnitConv([2, 0])


@pytest.fixture
def simple_element(x_device, y_device, mock_sim_data_source, unit_uc,
                   double_uc):
    # A unit conversion object that returns the same as the input.
    element = Element('element1', 0, 'BPM', 0.0, cell=1)
    element.add_to_family('family')
    element.set_data_source(DeviceDataSource(), pytac.LIVE)
    element.add_device('x', x_device, unit_uc)
    element.add_device('y', y_device, double_uc)
    element.set_data_source(mock_sim_data_source, pytac.SIM)
    return element


@pytest.fixture
def simple_lattice(simple_element, x_device, y_device, mock_sim_data_source,
                   unit_uc, double_uc):
    lattice = Lattice(LATTICE_NAME)
    lattice.add_element(simple_element)
    lattice.set_data_source(DeviceDataSource(), pytac.LIVE)
    lattice.add_device('x', x_device, unit_uc)
    lattice.add_device('y', y_device, double_uc)
    lattice.set_data_source(mock_sim_data_source, pytac.SIM)
    return lattice


@pytest.fixture
def simple_data_source_manager(x_device, y_device, mock_sim_data_source,
                               unit_uc, double_uc):
    data_source_manager = DataSourceManager()
    data_source_manager.set_data_source(DeviceDataSource(), pytac.LIVE)
    data_source_manager.add_device('x', x_device, unit_uc)
    data_source_manager.add_device('y', y_device, double_uc)
    data_source_manager.set_data_source(mock_sim_data_source, pytac.SIM)
    return data_source_manager


@pytest.fixture(scope="session")
def vmx_ring():
    return pytac.load_csv.load('VMX', mock.MagicMock)


@pytest.fixture(scope="session")
def diad_ring():
    return pytac.load_csv.load('DIAD', mock.MagicMock)


@pytest.fixture
def lattice():
    lat = load_csv.load('dummy', mock.MagicMock(), os.path.join(CURRENT_DIR,
                                                                'data'))
    return lat


@pytest.fixture
def mock_cs():
    cs = mock.MagicMock()
    cs.get.return_value = DUMMY_ARRAY
    return cs


@pytest.fixture
def simple_epics_element(mock_cs, unit_uc):
    element = EpicsElement(1, 0, 'BPM', 0.0, cell=1)
    x_device = EpicsDevice('x_device', mock_cs, True, RB_PV, SP_PV)
    y_device = EpicsDevice('y_device', mock_cs, True, SP_PV, RB_PV)
    element.add_to_family('family')
    element.set_data_source(DeviceDataSource(), pytac.LIVE)
    element.add_device('x', x_device, unit_uc)
    element.add_device('y', y_device, unit_uc)
    return element


@pytest.fixture
def simple_epics_lattice(simple_epics_element, mock_cs):
    lat = EpicsLattice('lattice', mock_cs)
    lat.add_element(simple_epics_element)
    return lat
