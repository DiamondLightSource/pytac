from pytac.exceptions import PvException
import pytac.element
import pytac.device
from pytac.units import PolyUnitConv
import pytest
import mock
import pytac


PREFIX = 'prefix'
RB_SUFF = ':rb'
RB_PV = PREFIX + RB_SUFF
SP_SUFF = ':sp'
SP_PV = PREFIX + SP_SUFF

DUMMY_VALUE_1 = 40.0
DUMMY_VALUE_2 = 4.7
DUMMY_VALUE_3 = -6


def mock_uc():
    uc = mock.MagicMock()
    uc.phys_to_eng.return_value = DUMMY_VALUE_2
    uc.eng_to_phys.return_value = DUMMY_VALUE_3
    return uc


@pytest.fixture
def test_element(length=0.0, uc=mock_uc()):
    mock_cs = mock.MagicMock()
    mock_cs.get.return_value = DUMMY_VALUE_1

    element = pytac.element.Element('dummy', 1.0, 'Quad')
    device1 = pytac.device.Device(PREFIX, mock_cs, True, RB_SUFF, SP_SUFF)
    device2 = pytac.device.Device(PREFIX, mock_cs, True, SP_SUFF, RB_SUFF)

    element.add_device('x', device1, uc)
    element.add_device('y', device2, uc)

    mock_model = mock.MagicMock()
    mock_model.get_value.return_value = DUMMY_VALUE_2
    element.set_model(mock_model)

    return element


def test_create_element():
    e = pytac.element.Element('bpm1', 6.0, 'bpm')
    e.add_to_family('BPM')
    assert 'BPM' in e.families
    assert e.length == 6.0


def test_add_element_to_family():
    e = pytac.element.Element('dummy', 6.0, 'Quad')
    e.add_to_family('fam')
    assert 'fam' in e.families


def test_get_device_raises_KeyError_if_device_not_present(test_element):
    with pytest.raises(KeyError):
        test_element.get_device('not-a-device')


def test_get_value_uses_cs_if_model_live(test_element):
    test_element.get_value('x', handle=pytac.SP, model=pytac.LIVE)
    test_element.get_device('x')._cs.get.assert_called_with(SP_PV)
    test_element.get_value('x', handle=pytac.RB, model=pytac.LIVE)
    test_element.get_device('x')._cs.get.assert_called_with(RB_PV)


def test_get_value_uses_uc_if_necessary_for_cs_call(test_element):
    test_element.get_value('x', handle=pytac.SP, unit=pytac.PHYS, model=pytac.LIVE)
    test_element._uc['x'].eng_to_phys.assert_called_with(DUMMY_VALUE_1)
    test_element.get_device('x')._cs.get.assert_called_with(SP_PV)


def test_get_value_uses_uc_if_necessary_for_model_call(test_element):
    test_element.get_value('x', handle=pytac.SP, unit=pytac.ENG, model=pytac.SIM)
    test_element._uc['x'].phys_to_eng.assert_called_with(DUMMY_VALUE_2)
    test_element._model.get_value.assert_called_with('x')


@pytest.mark.parametrize('pv_type', ['readback', 'setpoint'])
def test_get_pv_name(pv_type, test_element):
    assert isinstance(test_element.get_pv_name('x'), list)
    assert isinstance(test_element.get_pv_name('y'), list)
    assert isinstance(test_element.get_pv_name('x', pv_type), str)
    assert isinstance(test_element.get_pv_name('y', pv_type), str)


def test_set_value(test_element):
    test_element.set_value('x', DUMMY_VALUE_2)
    test_element.get_device('x')._cs.put.assert_called_with(SP_PV, DUMMY_VALUE_2)

    test_element.set_value('x', DUMMY_VALUE_2, unit=pytac.PHYS)
    test_element.get_device('x')._cs.put.assert_called_with(SP_PV, DUMMY_VALUE_2)

    with pytest.raises(PvException):
        test_element.set_value('non_existent', 40.0)


def test_get_pv_exceptions(test_element):
    with pytest.raises(PvException):
        test_element.get_value('setpoint', 'unknown_field')
    with pytest.raises(PvException):
        test_element.get_value('unknown_handle', 'y')
    with pytest.raises(PvException):
        test_element.get_pv_name('unknown_handle')


def test_identity_conversion():
    uc_id = PolyUnitConv([1, 0])
    element = test_element(uc=uc_id)
    value_physics = element.get_value('x', 'setpoint', pytac.PHYS)
    value_machine = element.get_value('x', 'setpoint', pytac.ENG)
    assert value_machine == DUMMY_VALUE_1
    assert value_physics == 40.0


def test_get_fields(test_element):
    assert set(test_element.get_fields()) == set(['y', 'x'])

def test_element_representation(test_element):
    s = str(test_element)
    assert test_element.name in s
    assert str(test_element.length) in s
    for f in test_element.families:
        assert f in s
