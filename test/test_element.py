import pytest

from constants import DUMMY_VALUE_1, DUMMY_VALUE_2
import pytac
import pytac.device


def test_create_element():
    e = pytac.element.Element('bpm1', 6.0, 'bpm', 0.0)
    e.add_to_family('BPM')
    assert 'BPM' in e.families
    assert e.length == 6.0


def test_add_element_to_family():
    e = pytac.element.Element('dummy', 6.0, 'Quad', 0.0)
    e.add_to_family('fam')
    assert 'fam' in e.families


def test_device_methods_raise_DataSourceException_if_no_device_data_sorce(simple_element):
    basic_element = simple_element
    del basic_element._data_source_manager._data_sources[pytac.LIVE]
    d = pytac.device.BasicDevice(0)
    uc = pytac.units.NullUnitConv()
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_element.add_device('x', d, uc)
    with pytest.raises(pytac.exceptions.DataSourceException):
        basic_element.get_device('x')


def test_get_device_raises_KeyError_if_device_not_present(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.get_device('not-a-device')


def test_get_unitconv_returns_unitconv_object(simple_element, unit_uc,
                                              double_uc):
    assert simple_element.get_unitconv('x') == unit_uc
    assert simple_element.get_unitconv('y') == double_uc


def test_get_unitconv_raises_FieldException_if_device_not_present(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.get_unitconv('not-a-device')


def test_get_value_uses_uc_if_necessary_for_cs_call(simple_element, double_uc):
    simple_element._data_source_manager._uc['x'] = double_uc
    assert simple_element.get_value('x', handle=pytac.SP, units=pytac.PHYS,
                                    data_source=pytac.LIVE) == (DUMMY_VALUE_1 * 2)


def test_get_value_uses_uc_if_necessary_for_sim_call(simple_element, double_uc):
    simple_element._data_source_manager._uc['x'] = double_uc
    assert simple_element.get_value('x', handle=pytac.SP, data_source=pytac.SIM,
                                    units=pytac.ENG) == (DUMMY_VALUE_2 / 2)
    simple_element._data_source_manager._data_sources[pytac.SIM].get_value.assert_called_with('x', pytac.SP)


def test_set_value_eng(simple_element):
    simple_element.set_value('x', DUMMY_VALUE_2, handle=pytac.SP)
    # No conversion needed
    simple_element.get_device('x').set_value.assert_called_with(DUMMY_VALUE_2)


def test_set_value_phys(simple_element, double_uc):
    simple_element._data_source_manager._uc['x'] = double_uc
    simple_element.set_value('x', DUMMY_VALUE_2, handle=pytac.SP,
                             units=pytac.PHYS)
    # Conversion fron physics to engineering units
    simple_element.get_device('x').set_value.assert_called_with(DUMMY_VALUE_2 / 2)


def test_set_exceptions(simple_element, unit_uc):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.set_value('unknown_field', 40.0, 'setpoint')
    with pytest.raises(pytac.exceptions.HandleException):
        simple_element.set_value('y', 40.0, 'unknown_handle')
    with pytest.raises(pytac.exceptions.DataSourceException):
        simple_element.set_value('y', 40.0, 'setpoint',
                                 data_source='unknown_data_source')
    simple_element._data_source_manager._uc['uc_but_not_data_source_field'] = unit_uc
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.set_value('uc_but_not_data_source_field', 40.0,
                                 'setpoint')


def test_get_exceptions(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.get_value('unknown_field', 'setpoint')
    with pytest.raises(pytac.exceptions.DataSourceException):
        simple_element.get_value('y', 'setpoint',
                                 data_source='unknown_data_source')


def test_identity_conversion(simple_element):
    value_physics = simple_element.get_value('x', 'setpoint', pytac.PHYS)
    value_machine = simple_element.get_value('x', 'setpoint', pytac.ENG)
    assert value_machine == DUMMY_VALUE_1
    assert value_physics == DUMMY_VALUE_1


def test_get_fields(simple_element):
    assert set(simple_element.get_fields()[pytac.LIVE]) == set(['y', 'x'])


def test_element_representation(simple_element):
    s = str(simple_element)
    assert simple_element.name in s
    assert str(simple_element.length) in s
    for f in simple_element.families:
        assert f in s
