import mock
import pytac
import pytest
from pytac.epics import EpicsDevice, PvEnabler
from pytac.exceptions import HandleException
from constants import PREFIX, RB_PV, SP_PV


def create_epics_device(prefix=PREFIX, rb_pv=RB_PV, sp_pv=SP_PV, enabled=True):
    mock_cs = mock.MagicMock()
    mock_cs.get.return_value = 1.0
    device = EpicsDevice(prefix, mock_cs, enabled=enabled, rb_pv=rb_pv,
                         sp_pv=sp_pv)
    return device


def test_set_epics_device_value():
    device = create_epics_device()
    device.set_value(40)
    device._cs.put.assert_called_with(SP_PV, 40)


def test_get_epics_device_value():
    device = create_epics_device()
    assert device.get_value(pytac.SP)==1.0


def test_epics_device_invalid_sp_raises_exception():
    device2 = create_epics_device(PREFIX, RB_PV, None)
    with pytest.raises(HandleException):
        device2.set_value(40)


def test_get_epics_device_value_invalid_handle_raises_exception():
    device = create_epics_device()
    with pytest.raises(HandleException):
        device.get_value('non_existent')


def test_epics_device_is_enabled_by_default():
    device = create_epics_device()
    assert device.is_enabled()


def test_epics_device_is_disabled_if_False_enabler():
    device = create_epics_device(enabled=False)
    assert not device.is_enabled()


def test_epics_device_is_enabled_returns_bool_value():
    device = create_epics_device(enabled=mock.MagicMock())
    assert device.is_enabled() is True


def test_PvEnabler():
    mock_cs = mock.MagicMock()
    mock_cs.get.return_value = '40'
    pve = PvEnabler('enable-pv', '40', mock_cs)
    assert pve
    mock_cs.get.return_value = 50
    assert not pve
