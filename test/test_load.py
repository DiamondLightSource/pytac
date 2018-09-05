import pytac
import pytest
from mock import patch
from pytac.load_csv import load
from pytac.exceptions import LatticeException


def test_control_system_is_None_import():
    class CothreadControlSystem():
        pass
    with patch('pytac.cothread_cs.CothreadControlSystem', CothreadControlSystem):
        assert bool(load('VMX'))
        assert isinstance(load('VMX')._cs, pytac.cothread_cs.CothreadControlSystem)


def test_LatticeException_is_raised_when_import_fails():
    def CothreadControlSystem():
        raise ImportError
    with patch('pytac.cothread_cs.CothreadControlSystem', CothreadControlSystem):
        with pytest.raises(LatticeException):
            load('VMX')


def test_elements_loaded(lattice):
    assert len(lattice) == 4
    assert len(lattice.get_elements('drift')) == 2
    assert len(lattice.get_elements('no_family')) == 0
    assert lattice.get_length() == 2.6


def test_element_details_loaded(lattice):
    quad = lattice.get_elements('quad')[0]
    assert quad.cell == 1
    assert quad.s == 1.0
    assert quad.index == 2


def test_devices_loaded(lattice):
    quads = lattice.get_elements('quad')
    assert len(quads) == 1
    assert quads[0].get_pv_name(field='b1', handle='readback') == 'Q1:RB'
    assert quads[0].get_pv_name(field='b1', handle='setpoint') == 'Q1:SP'


def test_families_loaded(lattice):
    assert lattice.get_all_families() == set(['drift', 'sext', 'quad',
                                              'ds', 'qf', 'qs', 'sd'])
    assert lattice.get_elements('quad')[0].families == set(('quad', 'qf', 'qs'))
