import pytest

from pytac import cs, data_source, device


def test_control_system_throws_not_implemented_error():
    test_cs = cs.ControlSystem()
    with pytest.raises(NotImplementedError):
        test_cs.get_single("dummy", "throw")
    with pytest.raises(NotImplementedError):
        test_cs.get_multiple(["dummy1", "dummy_2"], "throw")
    with pytest.raises(NotImplementedError):
        test_cs.set_single("dummy", 1, "throw")
    with pytest.raises(NotImplementedError):
        test_cs.set_multiple(["dummy_1", "dummy_2"], [1, 2], "throw")


def test_data_source_throws_not_implemented_error():
    test_ds = data_source.DataSource()
    with pytest.raises(NotImplementedError):
        test_ds.get_fields()
    with pytest.raises(NotImplementedError):
        test_ds.get_value("field", "handle", "throw")
    with pytest.raises(NotImplementedError):
        test_ds.set_value("field", 0.0, "throw")


def test_device_throws_not_implemented_error():
    test_d = device.Device()
    with pytest.raises(NotImplementedError):
        test_d.is_enabled()
    with pytest.raises(NotImplementedError):
        test_d.set_value(0.0, "throw")
    with pytest.raises(NotImplementedError):
        test_d.get_value("handle", "throw")
