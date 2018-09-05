import os
import sys
import pytac
import pytest
from pytac.load_csv import load
from pytac.exceptions import LatticeException


def test_control_system_is_None_import():
    # Temporarily edit cothread_cs to use a mock so this test works with Travis.
    os.rename(os.path.join(os.path.realpath('.'), 'pytac/cothread_cs.py'),
              "pytac/placeholder.py")
    f = open("pytac/cothread_cs.py", "w+")
    f.write("import mock\n\nclass CothreadControlSystem():\n    mock.MagicMock")
    f.close()
    # Assert lattice is loaded when LatticeException is not raised.
    assert bool(load('VMX'))
    # Assert that the default lattice control system is Cothread.
    assert isinstance(load('VMX')._cs, pytac.cothread_cs.CothreadControlSystem)
    # Change Cothread_cs back to how it was before.
    os.remove("pytac/cothread_cs.py")
    os.rename(os.path.join(os.path.realpath('.'), 'pytac/placeholder.py'),
              "pytac/cothread_cs.py")


def test_LatticeException_is_raised_when_import_fails():
    # Temporarily edit cothread_cs to always raise an ImportError.
    os.rename(os.path.join(os.path.realpath('.'), 'pytac/cothread_cs.py'),
              "pytac/placeholder.py")
    f = open("pytac/cothread_cs.py", "w+")
    f.write("import not_a_module\n\nclass CothreadControlSystem():\n   pass")
    f.close()
    # Check LatticeException is correctly raised when import fails.
    cothread = getattr(pytac, "cothread_cs")
    delattr(pytac, "cothread_cs")
    del sys.modules['pytac.cothread_cs']
    with pytest.raises(LatticeException):
        load('VMX')
    setattr(pytac, "cothread_cs", cothread)
    # Change Cothread_cs back to how it was before.
    os.remove("pytac/cothread_cs.py")
    os.rename(os.path.join(os.path.realpath('.'), 'pytac/placeholder.py'),
              "pytac/cothread_cs.py")


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
