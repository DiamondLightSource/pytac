import numpy
import pytest
import pytac
from constants import DUMMY_ARRAY, RB_PV, SP_PV


def test_get_values(simple_epics_lattice):
    simple_epics_lattice.get_element_values('family', 'x', pytac.RB)
    simple_epics_lattice._cs.get_multiple.assert_called_with([RB_PV])


def test_set_values(simple_epics_lattice):
    simple_epics_lattice.set_element_values('family', 'x', [1])
    simple_epics_lattice._cs.set_multiple.assert_called_with([SP_PV], [1])


@pytest.mark.parametrize('dtype, expected',
                         ((numpy.float64, numpy.array(DUMMY_ARRAY,
                                                      dtype=numpy.float64)),
                          (numpy.int32, numpy.array(DUMMY_ARRAY,
                                                    dtype=numpy.int32)),
                          (numpy.bool_, numpy.array(DUMMY_ARRAY,
                                                    dtype=numpy.bool_)),
                          (None, DUMMY_ARRAY)))
def test_get_values_returns_numpy_array_if_requested(simple_epics_lattice,
                                                     dtype, expected):
    values = simple_epics_lattice.get_element_values('family', 'x', pytac.RB,
                                                     dtype=dtype)
    numpy.testing.assert_equal(values, expected)
    simple_epics_lattice._cs.get_multiple.assert_called_with([RB_PV])


@pytest.mark.parametrize('pv_type', ['readback', 'setpoint'])
def test_get_element_pv_name(pv_type, simple_epics_element):
    assert isinstance(simple_epics_element.get_pv_name('x', pv_type), str)
    assert isinstance(simple_epics_element.get_pv_name('y', pv_type), str)
    with pytest.raises(pytac.exceptions.DeviceException):
        simple_epics_element.get_pv_name('not_a_field', pv_type)


@pytest.mark.parametrize('pv_type', ['readback', 'setpoint'])
def test_get_pv_name(pv_type, simple_epics_lattice):
    assert isinstance(simple_epics_lattice.get_pv_name('x', pv_type), str)
    assert isinstance(simple_epics_lattice.get_pv_name('y', pv_type), str)
    with pytest.raises(pytac.exceptions.DeviceException):
        simple_epics_lattice.get_pv_name('not_a_field', pv_type)


def test_get_value_uses_cs_if_data_source_live(simple_epics_element):
    simple_epics_element.get_value('x', handle=pytac.SP, data_source=pytac.LIVE)
    simple_epics_element.get_device('x')._cs.get_single.assert_called_with(SP_PV)
    simple_epics_element.get_value('x', handle=pytac.RB, data_source=pytac.LIVE)
    simple_epics_element.get_device('x')._cs.get_single.assert_called_with(RB_PV)


def test_get_value_raises_HandleExceptions(simple_epics_element):
    with pytest.raises(pytac.exceptions.HandleException):
        simple_epics_element.get_value('y', 'unknown_handle')


def test_get_pv_name_raises_DeviceException(simple_epics_element):
    with pytest.raises(pytac.exceptions.DeviceException):
        simple_epics_element.get_pv_name('unknown_field', 'setpoint')


def test_set_values_raises_LatticeException(simple_epics_lattice):
    with pytest.raises(ValueError):
        simple_epics_lattice.set_element_values('family', 'x', [1, 2])
    with pytest.raises(ValueError):
        simple_epics_lattice.set_element_values('family', 'x', [])
