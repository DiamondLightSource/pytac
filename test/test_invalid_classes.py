import pytest

from pytac import cs, data_source, device


def test_ControlSystem_throws_NotImplementedError():
    test_cs = cs.ControlSystem()
    with pytest.raises(NotImplementedError):
        test_cs.get_single('dummy', 'throw')
    with pytest.raises(NotImplementedError):
        test_cs.get_multiple(['dummy1', 'dummy_2'], 'throw')
    with pytest.raises(NotImplementedError):
        test_cs.set_single('dummy', 1, 'throw')
    with pytest.raises(NotImplementedError):
        test_cs.set_multiple(['dummy_1', 'dummy_2'], [1, 2], 'throw')


def test_DataSource_throws_NotImplementedError():
    test_ds = data_source.DataSource()
    with pytest.raises(NotImplementedError):
        test_ds.get_fields()
    with pytest.raises(NotImplementedError):
        test_ds.get_value('field', 'handle', 'throw')
    with pytest.raises(NotImplementedError):
        test_ds.set_value('field', 0.0, 'throw')


def test_Device_throws_NotImplementedError():
    test_d = device.Device()
    with pytest.raises(NotImplementedError):
        test_d.is_enabled()
    with pytest.raises(NotImplementedError):
        test_d.set_value(0.0, 'throw')
    with pytest.raises(NotImplementedError):
        test_d.get_value('handle', 'throw')
