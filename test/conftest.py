import mock
import pytest
import pytac
from pytac.element import Element
from pytac.model import DeviceModel
from pytac.units import PolyUnitConv

from constants import DUMMY_VALUE_1, DUMMY_VALUE_2, SP_PV


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
    # Create mock devices and attach them to the element
    x_device = mock.MagicMock()
    x_device.name = 'x_device'
    x_device.get_value.return_value = DUMMY_VALUE_1
    y_device = mock.MagicMock()
    y_device.name = 'y_device'
    y_device.get_pv_name.return_value = SP_PV
    element.add_to_family('family')

    element.set_model(DeviceModel(), pytac.LIVE)
    element.add_device('x', x_device, unit_uc)
    element.add_device('y', y_device, unit_uc)

    # Add mock sim model
    mock_sim_model = mock.MagicMock()
    mock_sim_model.get_value.return_value = DUMMY_VALUE_2
    mock_sim_model.units = pytac.PHYS
    element.set_model(mock_sim_model, pytac.SIM)

    return element

