from pytac.exceptions import DataSourceException
from unittest import mock

import pytest

from constants import PREFIX, RB_PV, SP_PV
import pytac
from pytac.device import SimpleDevice, EpicsDevice, PvEnabler


def create_epics_device(prefix=PREFIX, rb_pv=RB_PV, sp_pv=SP_PV, enabled=True):
    mock_cs = mock.MagicMock()
    mock_cs.get_single.return_value = 40.0
    device = EpicsDevice(prefix, mock_cs, enabled=enabled, rb_pv=rb_pv, sp_pv=sp_pv)
    return device


def create_simple_device(value=1.0, enabled=True):
    device = SimpleDevice(value, enabled, False)
    return device


# Epics device specific tests.
def test_set_epics_device_value():
    device = create_epics_device()
    device.set_value(40)
    device._cs.set_single.assert_called_with(SP_PV, 40, True)


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
        device.get_value("non_existent")


# Simple device specific tests.
def test_set_simple_device_value():
    device = create_simple_device()
    device.set_value(40)
    assert device.value == 40


def test_get_simple_device_value_without_handle():
    device = create_simple_device()
    assert device.get_value() == 1.0


def test_get_simple_device_value_with_handle():
    device = create_simple_device()
    assert device.get_value(handle=pytac.RB) == 1.0


def test_simple_device_raises_DataSourceException_if_readonly_and_set_value_called():
    device = SimpleDevice(10, readonly=True)
    with pytest.raises(DataSourceException):
        device.set_value(4)


# Generalised device tests.
@pytest.mark.parametrize(
    "device_creation_function", [create_epics_device, create_simple_device]
)
def test_device_is_enabled_by_default(device_creation_function):
    device = device_creation_function()
    assert device.is_enabled()


@pytest.mark.parametrize(
    "device_creation_function", [create_epics_device, create_simple_device]
)
def test_device_is_disabled_if_False_enabler(device_creation_function):
    device = device_creation_function(enabled=False)
    assert not device.is_enabled()


@pytest.mark.parametrize(
    "device_creation_function", [create_epics_device, create_simple_device]
)
def test_device_is_enabled_returns_bool_value(device_creation_function):
    device = device_creation_function(enabled=1)
    assert device.is_enabled() is True


# PvEnabler test.
def test_PvEnabler(mock_cs):
    pve = PvEnabler("enable-pv", 40, mock_cs)
    assert pve
    mock_cs.get_single.return_value = 50
    assert not pve
