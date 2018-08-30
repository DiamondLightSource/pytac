import pytest
import pytac
from constants import DUMMY_VALUE_2


#not a test function.
def param_switch(simple_element, simple_lattice, param):
    if param=='element':
        return simple_element
    elif param=='lattice':
        return simple_lattice


@pytest.mark.parametrize('param', ['element', 'lattice'])
def test_get_device(simple_element, simple_lattice, param, y_device):
    simple_object = param_switch(simple_element, simple_lattice, param)
    assert simple_object.get_device('y')==y_device


@pytest.mark.parametrize('param', ['element', 'lattice'])
def test_get_unitconv(simple_element, simple_lattice, param, unit_uc):
    simple_object = param_switch(simple_element, simple_lattice, param)
    assert simple_object.get_unitconv('x')==unit_uc


@pytest.mark.parametrize('param', ['element', 'lattice'])
def test_get_fields(simple_element, simple_lattice, param):
    simple_object = param_switch(simple_element, simple_lattice, param)
    fields = simple_object.get_fields()[pytac.LIVE]
    assert len(fields)==2
    assert 'x' and 'y' in fields


@pytest.mark.parametrize('param', ['element', 'lattice'])
def test_set_value(simple_element, simple_lattice, param):
    simple_object = param_switch(simple_element, simple_lattice, param)
    simple_object.set_value('x', DUMMY_VALUE_2, pytac.SP, pytac.ENG, pytac.LIVE)
    simple_object.get_device('x').set_value.assert_called_with(DUMMY_VALUE_2)


@pytest.mark.parametrize('param', ['element', 'lattice'])
def test_get_value_sim(simple_element, simple_lattice, param):
    simple_object = param_switch(simple_element, simple_lattice, param)
    assert simple_object.get_value('x', pytac.RB, pytac.PHYS, pytac.SIM)==DUMMY_VALUE_2


@pytest.mark.parametrize('param', ['element', 'lattice'])
def test_unit_conversion(simple_element, simple_lattice, param, double_uc):
    simple_object = param_switch(simple_element, simple_lattice, param)
    simple_object._data_source_manager._uc['y'] = double_uc
    simple_object.set_value('y', DUMMY_VALUE_2, pytac.SP, pytac.PHYS, pytac.LIVE)
    simple_object.get_device('y').set_value.assert_called_with((DUMMY_VALUE_2 / 2))
