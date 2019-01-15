import mock
import pytest

from constants import PREFIX, RB_PV, SP_PV
import pytac
from pytac.device import BasicDevice, EpicsDevice, PvEnabler


# Not a test - epics device creation function used in tests.
def create_epics_device(prefix=PREFIX, rb_pv=RB_PV, sp_pv=SP_PV, enabled=True):
    mock_cs = mock.MagicMock()
    mock_cs.get_single.return_value = 40.0
    device = EpicsDevice(prefix, mock_cs, enabled=enabled, rb_pv=rb_pv,
                         sp_pv=sp_pv)
    return device


# Not a test - basic device creation function used in tests.
def create_basic_device(value=1.0, enabled=True):
    device = BasicDevice(value, enabled)
    return device


# Epics device specific tests.
def test_set_epics_device_value():
    device = create_epics_device()
    device.set_value(40)
    device._cs.set_single.assert_called_with(SP_PV, 40)


def test_get_epics_device_value():
    device = create_epics_device()
    assert device.get_value(pytac.SP) == 40.0


def test_epics_device_invalid_sp_raises_exception():
    device2 = create_epics_device(PREFIX, RB_PV, None)
    with pytest.raises(pytac.exceptions.HandleException):
        device2.set_value(40)


def test_get_epics_device_value_invalid_handle_raises_exception():
    device = create_epics_device()
    with pytest.raises(pytac.exceptions.HandleException):
        device.get_value('non_existent')


# Basic device specific tests.
def test_set_basic_device_value():
    device = create_basic_device()
    device.set_value(40)
    assert device.value == 40


def test_get_basic_device_value_without_handle():
    device = create_basic_device()
    assert device.get_value() == 1.0


def test_get_basic_device_value_with_handle():
    device = create_basic_device()
    assert device.get_value(handle=pytac.RB) == 1.0


# Generalised device tests.
@pytest.mark.parametrize('device_creation_function', [create_epics_device,
                         create_basic_device])
def test_device_is_enabled_by_default(device_creation_function):
    device = device_creation_function()
    assert device.is_enabled()


@pytest.mark.parametrize('device_creation_function', [create_epics_device,
                         create_basic_device])
def test_device_is_disabled_if_False_enabler(device_creation_function):
    device = device_creation_function(enabled=False)
    assert not device.is_enabled()


@pytest.mark.parametrize('device_creation_function', [create_epics_device,
                         create_basic_device])
def test_device_is_enabled_returns_bool_value(device_creation_function):
    device = device_creation_function(enabled=1)
    assert device.is_enabled() is True


# PvEnabler test.
def test_PvEnabler():
    mock_cs = mock.MagicMock()
    mock_cs.get_single.return_value = 40.0
    pve = PvEnabler('enable-pv', 40, mock_cs)
    assert pve
    mock_cs.get_single.return_value = 50
    assert not pve
