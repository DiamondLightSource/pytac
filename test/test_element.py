import pytac.epics
import pytac.device
import pytest
import pytac
from constants import DUMMY_VALUE_1, DUMMY_VALUE_2


def test_create_element():
    e = pytac.element.Element('bpm1', 6.0, 'bpm')
    e.add_to_family('BPM')
    assert 'BPM' in e.families
    assert e.length == 6.0


def test_add_element_to_family():
    e = pytac.element.Element('dummy', 6.0, 'Quad')
    e.add_to_family('fam')
    assert 'fam' in e.families


def test_get_device_raises_KeyError_if_device_not_present(simple_element):
    with pytest.raises(KeyError):
        simple_element.get_device('not-a-device')


def test_get_unitconv_returns_unitconv_object(simple_element, unit_uc):
    assert simple_element.get_unitconv('x') == unit_uc
    assert simple_element.get_unitconv('y') == unit_uc


def test_get_unitconv_raises_KeyError_if_device_not_present(simple_element):
    with pytest.raises(KeyError):
        simple_element.get_unitconv('not-a-device')


def test_get_value_uses_uc_if_necessary_for_cs_call(simple_element, double_uc):
    simple_element._data_source_manager._uc['x'] = double_uc
    assert simple_element.get_value('x', handle=pytac.SP, units=pytac.PHYS,
                                    model=pytac.LIVE) == (DUMMY_VALUE_1 * 2)


def test_get_value_uses_uc_if_necessary_for_sim_call(simple_element, double_uc):
    simple_element._data_source_manager._uc['x'] = double_uc
    assert simple_element.get_value('x', handle=pytac.SP, units=pytac.ENG,
                                    model=pytac.SIM) == (DUMMY_VALUE_2 / 2)
    simple_element._data_source_manager._models[pytac.SIM].get_value.assert_called_with('x', pytac.SP)


def test_set_value_eng(simple_element):
    simple_element.set_value('x', DUMMY_VALUE_2)
    # No conversion needed
    simple_element.get_device('x').set_value.assert_called_with(DUMMY_VALUE_2)


def test_set_value_phys(simple_element, double_uc):
    simple_element._data_source_manager._uc['x'] = double_uc
    simple_element.set_value('x', DUMMY_VALUE_2, units=pytac.PHYS)
    # Conversion fron physics to engineering units
    simple_element.get_device('x').set_value.assert_called_with((DUMMY_VALUE_2 / 2))


def test_set_exceptions(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.set_value('unknown_field', 40.0, 'setpoint')
    with pytest.raises(pytac.exceptions.HandleException):
        simple_element.set_value('y', 40.0, 'unknown_handle')
    with pytest.raises(pytac.exceptions.DeviceException):
        simple_element.set_value('y', 40.0, 'setpoint', model='unknown_model')


def test_get_exceptions(simple_element):
    with pytest.raises(pytac.exceptions.FieldException):
        simple_element.get_value('unknown_field', 'setpoint')
    with pytest.raises(pytac.exceptions.DeviceException):
        simple_element.get_value('y', 'setpoint', model='unknown_model')


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
