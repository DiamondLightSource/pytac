import sys
import pytac
import pytest
from mock import patch
from types import ModuleType
from pytac.load_csv import load
from pytac.exceptions import LatticeException


@pytest.fixture
def Travis_CI_compatability():
    class catools(object):
        def caget():
            pass

        def caput():
            pass

    cothread = ModuleType('cothread')
    cothread.catools = catools
    sys.modules['cothread'] = cothread
    sys.modules['cothread.catools'] = catools


@pytest.fixture
def mock_control_system():
    # Can't make class fixtures so have to hide class inside a function.
    class CothreadControlSystem():
        pass
    return CothreadControlSystem


@pytest.fixture
def mock_ImportError():
    # function not a class to stop it raising ImportError during compile.
    def CothreadControlSystem():
        raise ImportError
    return CothreadControlSystem


def test_default_control_system_import(Travis_CI_compatability, mock_control_system):
    #Travis_CI_compatability
    with patch('pytac.cothread_cs.CothreadControlSystem', mock_control_system):
        assert bool(load('VMX'))
        assert isinstance(load('VMX')._cs, pytac.cothread_cs.CothreadControlSystem)


def test_LatticeException_is_raised_when_import_fails(Travis_CI_compatability, mock_ImportError):
    #Travis_CI_compatability
    with patch('pytac.cothread_cs.CothreadControlSystem', mock_ImportError):
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
