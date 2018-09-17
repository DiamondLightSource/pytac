import pytest
from pytac import cs, data_source, device


def test_ControlSystem_throws_NotImplementedError():
    test_cs = cs.ControlSystem()
    with pytest.raises(NotImplementedError):
        test_cs.get('dummy')
    with pytest.raises(NotImplementedError):
        test_cs.put('dummy', 1)


def test_DataSource_throws_NotImplementedError():
    test_ds = data_source.DataSource()
    with pytest.raises(NotImplementedError):
        test_ds.get_fields()
    with pytest.raises(NotImplementedError):
        test_ds.get_value('field', 'handle')
    with pytest.raises(NotImplementedError):
        test_ds.set_value('field', 0.0)


def test_Device_throws_NotImplementedError():
    test_d = device.Device()
    with pytest.raises(NotImplementedError):
        test_d.is_enabled()
    with pytest.raises(NotImplementedError):
        test_d.set_value(0.0)
    with pytest.raises(NotImplementedError):
        test_d.get_value()
