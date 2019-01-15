import os
import mock
import pytest
import sys
import types

import pytac
from pytac import load_csv
from pytac.element import Element, EpicsElement
from pytac.lattice import Lattice, EpicsLattice
from pytac.data_source import DataSourceManager, DeviceDataSource
from pytac.units import PolyUnitConv
from pytac.device import EpicsDevice
from constants import DUMMY_VALUE_1, DUMMY_VALUE_2, RB_PV, SP_PV, LATTICE_NAME, CURRENT_DIR, DUMMY_ARRAY


def pytest_sessionstart():
    """Create a dummy cothread module.

    cothread is not trivial to import, so it is better to mock it before any
    tests run. In particular, we need catools (the module that pytac imports
    from cothread), including the functions that pytac explicitly imports
    (caget and caput).
    """
    class ca_nothing(Exception):
        """A minimal mock of the cothread ca_nothing exception class.
        """
        def __init__(self, name, errorcode=True):
            self.ok = errorcode
            self.name = name

    cothread = types.ModuleType('cothread')
    catools = types.ModuleType('catools')
    catools.caget = mock.MagicMock()
    catools.caput = mock.MagicMock()
    catools.ca_nothing = ca_nothing
    cothread.catools = catools

    sys.modules['cothread'] = cothread
    sys.modules['cothread.catools'] = catools


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
    mock_sim_data_source.units = pytac.PHYS
    mock_sim_data_source.get_value.return_value = DUMMY_VALUE_2
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


def set_func(pvs, values):
    if len(pvs) is not len(values):
        raise ValueError


@pytest.fixture
def mock_cs():
    cs = mock.MagicMock()
    cs.get_single.return_value = DUMMY_VALUE_1
    cs.get_multiple.return_value = DUMMY_ARRAY
    cs.set_multiple.side_effect = set_func
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
    x_device = EpicsDevice('x_device', mock_cs, True, RB_PV, SP_PV)
    y_device = EpicsDevice('y_device', mock_cs, True, SP_PV, RB_PV)
    lat.set_data_source(DeviceDataSource(), pytac.LIVE)
    lat.add_device('x', x_device, unit_uc)
    lat.add_device('y', y_device, unit_uc)
    return lat
