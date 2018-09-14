import pytest
from pytac import cs, data_source, device


class InvalidControlSystem(cs.ControlSystem):
    """
    Extends ControlSystem without implementing required methods.
    """
    def __init__(self):
        pass


def test_ControlSystem_throws_NotImplememtedError():
    with pytest.raises(NotImplementedError):
        cs.ControlSystem()


def test_InvalidControlSystem_throws_NotImplementedError():
    ics = InvalidControlSystem()
    with pytest.raises(NotImplementedError):
        ics.get('dummy')
    with pytest.raises(NotImplementedError):
        ics.put('dummy', 1)


def test_DataSource_NotImplementedError():
    ds = data_source.DataSource()
    with pytest.raises(NotImplementedError):
        ds.get_fields()
    with pytest.raises(NotImplementedError):
        ds.get_value('field', 'handle')
    with pytest.raises(NotImplementedError):
        ds.set_value('field', 0.0)


def test_Device_NotImplementedError():
    d = device.Device()
    with pytest.raises(NotImplementedError):
        d.is_enabled()
    with pytest.raises(NotImplementedError):
        d.set_value(0.0)
    with pytest.raises(NotImplementedError):
        d.get_value()
