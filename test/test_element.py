from pytac.exceptions import PvException
import pytac.element
import pytac.device
from pytac.units import PolyUnitConv
import pytest
import mock
import pytac


@pytest.fixture
def test_element(length=0.0, uc=PolyUnitConv([1, 0])):

    mock_cs = mock.MagicMock()
    mock_cs.get.return_value = 40.0

    element = pytac.element.Element('dummy', 1.0, 'Quad')
    rb_pv = 'SR22C-DI-EBPM-04:SA:X'
    sp_pv = 'SR22C-DI-EBPM-04:SA:Y'
    device1 = pytac.device.Device(mock_cs, True, rb_pv, sp_pv)
    device2 = pytac.device.Device(mock_cs, True, sp_pv, rb_pv)

    element.add_device('x', device1, uc)
    element.add_device('y', device2, uc)

    return element


def test_create_element():
    e = pytac.element.Element('bpm1', 6.0, 'bpm')
    e.add_to_family('BPM')
    assert 'BPM' in e.families
    assert e.get_length() == 6.0


def test_add_element_to_family():
    e = pytac.element.Element('dummy', 6.0, 'Quad')
    e.add_to_family('fam')
    assert 'fam' in e.families


@pytest.mark.parametrize('pv_type', ['readback', 'setpoint'])
def test_get_pv_value(pv_type, test_element):
    # Tests to get/set pv names and/or values
    # The default unit conversion is identity
    assert test_element.get_pv_value('x', pv_type, unit=pytac.PHYS) == 40.0
    assert test_element.get_pv_value('x', pv_type, unit=pytac.ENG) == 40.0
    assert test_element.get_pv_value('y', pv_type, unit=pytac.PHYS) == 40.0
    assert test_element.get_pv_value('y', pv_type, unit=pytac.ENG) == 40.0


@pytest.mark.parametrize('pv_type', ['readback', 'setpoint'])
def test_get_pv_name(pv_type, test_element):
    assert isinstance(test_element.get_pv_name('x'), list)
    assert isinstance(test_element.get_pv_name('y'), list)
    assert isinstance(test_element.get_pv_name('x', pv_type), str)
    assert isinstance(test_element.get_pv_name('y', pv_type), str)


def test_put_pv_value(test_element):
    test_element.put_pv_value('x', 40.3)
    test_element.get_device('x')._cs.put.assert_called_with('SR22C-DI-EBPM-04:SA:Y', 40.3)

    test_element.put_pv_value('x', 40.3, unit=pytac.PHYS)
    test_element.get_device('x')._cs.put.assert_called_with('SR22C-DI-EBPM-04:SA:Y', 40.3)

    with pytest.raises(PvException):
        test_element.put_pv_value('non_existent', 40.0)


def test_get_pv_exceptions(test_element):
    with pytest.raises(PvException):
        test_element.get_pv_value('setpoint', 'unknown_field')
    with pytest.raises(PvException):
        test_element.get_pv_value('unknown_handle', 'y')
    with pytest.raises(PvException):
        test_element.get_pv_name('unknown_handle')


def test_identity_conversion():
    uc_id = PolyUnitConv([1, 0])
    element = test_element(uc=uc_id)
    value_physics = element.get_pv_value('x', 'setpoint', pytac.PHYS)
    value_machine = element.get_pv_value('x', 'setpoint', pytac.ENG)
    assert value_machine == 40.0
    assert value_physics == 40.0


def test_get_fields(test_element):
    assert set(test_element.get_fields()) == set(['y', 'x'])

def test_element_representation(test_element):
    s = str(test_element)
    assert test_element._name in s
    assert str(test_element._length) in s
    for f in test_element.families:
        assert f in s
