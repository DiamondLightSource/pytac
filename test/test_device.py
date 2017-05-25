from pytac.exceptions import PvException
import pytac.device
import pytest
import mock


SP_PV = 'SR01A-PC-SQUAD-01:SETI'
RB_PV = 'SR01A-PC-SQUAD-01:I'

@pytest.fixture
def create_device(readback=RB_PV, setpoint=SP_PV):
    _rb = readback
    _sp = setpoint
    device = pytac.device.Device(rb_pv=_rb, sp_pv=_sp, cs=mock.MagicMock())
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


def test_is_enabled(create_device):
    assert create_device.is_enabled() == True


def test_set_enabled(create_device):
    create_device.set_enabled(False)
    assert create_device.is_enabled() == False


def test_PvEnabler():
    mock_cs = mock.MagicMock()
    mock_cs.get.return_value = 40
    pve = pytac.device.PvEnabler('enable-pv', 40, mock_cs)
    assert bool(pve) == True
    # mock_cs.get.assert_called_with(pve._pv)

    mock_cs.get.return_value = 50
    assert bool(pve) == False
