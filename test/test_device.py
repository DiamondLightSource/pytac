from pytac.exceptions import PvException
import pytac.device
import pytest
import mock


SP_PV = 'SR01A-PC-SQUAD-01:SETI'
RB_PV = 'SR01A-PC-SQUAD-01:I'
ENABLE_PV = 'SR01C-DI-EBPM-01:CF:ENABLED_S'
ENABLED_VALUE = '1.0'

@pytest.fixture
def create_device(readback=RB_PV, setpoint=SP_PV, _enable_pv=ENABLE_PV, _enabled_value=ENABLED_VALUE):
    _rb = readback
    _sp = setpoint
    mock_cs = mock.MagicMock()
    mock_cs.get.return_value = '1.0'
    if _enable_pv and _enabled_value:
        pve = pytac.device.PvEnabler(_enable_pv, _enabled_value, mock_cs)
        device = pytac.device.Device(cs=mock.MagicMock(), enabled=pve, rb_pv=_rb, sp_pv=_sp)
    else:
        device = pytac.device.Device(cs=mock.MagicMock(), enabled=True, rb_pv=_rb, sp_pv=_sp)
    return device


def test_set_device_value(create_device):
    create_device.put_value(40)
    create_device._cs.put.assert_called_with(SP_PV, 40)


def test_device_invalid_sp_raise_exception():
    device2 = create_device(RB_PV, None)
    with pytest.raises(PvException):
        device2.put_value(40)
    with pytest.raises(PvException):
        create_device(None, None)


def test_get_device_value(create_device):
    with pytest.raises(PvException):
        create_device.get_value('non_existent')


def test_is_enabled_empty_string():
    device = create_device(_enabled_value='')
    assert device.is_enabled()

def test_is_enabled(create_device):
    assert create_device.is_enabled()


def test_is_disabled():
    device = create_device(_enabled_value='3')
    assert not device.is_enabled()


def test_PvEnabler():
    mock_cs = mock.MagicMock()
    mock_cs.get.return_value = '40'
    pve = pytac.device.PvEnabler('enable-pv', '40', mock_cs)
    assert pve

    mock_cs.get.return_value = 50
    assert not pve
