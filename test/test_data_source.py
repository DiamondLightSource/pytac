import pytest
import pytac
from constants import DUMMY_VALUE_2


@pytest.mark.parametrize('simple_object',
                         [pytest.lazy_fixture('simple_element'),
                          pytest.lazy_fixture('simple_lattice'),
                          pytest.lazy_fixture('simple_data_source_manager')])
def test_get_device(simple_object, y_device):
    assert simple_object.get_device('y') == y_device


@pytest.mark.parametrize('simple_object',
                         [pytest.lazy_fixture('simple_element'),
                          pytest.lazy_fixture('simple_lattice'),
                          pytest.lazy_fixture('simple_data_source_manager')])
def test_get_unitconv(simple_object, unit_uc):
    assert simple_object.get_unitconv('x') == unit_uc


@pytest.mark.parametrize('simple_object',
                         [pytest.lazy_fixture('simple_element'),
                          pytest.lazy_fixture('simple_lattice'),
                          pytest.lazy_fixture('simple_data_source_manager')])
def test_get_fields(simple_object):
    fields = simple_object.get_fields()[pytac.LIVE]
    assert len(fields) == 2
    assert 'x' and 'y' in fields


@pytest.mark.parametrize('simple_object',
                         [pytest.lazy_fixture('simple_element'),
                          pytest.lazy_fixture('simple_lattice'),
                          pytest.lazy_fixture('simple_data_source_manager')])
def test_set_value(simple_object):
    simple_object.set_value('x', DUMMY_VALUE_2, pytac.SP, pytac.ENG, pytac.LIVE)
    simple_object.get_device('x').set_value.assert_called_with(DUMMY_VALUE_2)


@pytest.mark.parametrize('simple_object',
                         [pytest.lazy_fixture('simple_element'),
                          pytest.lazy_fixture('simple_lattice'),
                          pytest.lazy_fixture('simple_data_source_manager')])
def test_get_value_sim(simple_object):
    assert simple_object.get_value('x', pytac.RB, pytac.PHYS,
                                   pytac.SIM) == DUMMY_VALUE_2


@pytest.mark.parametrize('simple_object',
                         [pytest.lazy_fixture('simple_element'),
                          pytest.lazy_fixture('simple_lattice'),
                          pytest.lazy_fixture('simple_data_source_manager')])
def test_unit_conversion(simple_object, double_uc):
    simple_object.set_value('y', DUMMY_VALUE_2, pytac.SP, pytac.PHYS,
                            pytac.LIVE)
    simple_object.get_device('y').set_value.assert_called_with((DUMMY_VALUE_2 / 2))
