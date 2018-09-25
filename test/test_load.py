import sys
import pytac
import pytest
from mock import patch, MagicMock
from types import ModuleType
from pytac.load_csv import load
from pytac.exceptions import LatticeException
from constants import DUMMY_VALUE_1, DUMMY_VALUE_2


@pytest.fixture(scope="session")
def Travis_CI_compatibility():
    # Cothread
    """Travis CI cannot import cothread so we must create a mock of cothread and
        catools (the module that pytac imports from cothread), including the
        functions that pytac explicitly imports (caget and caput).
       First we create a return function that depending on it's input specifies
        what our new caget will return. Then we make a MagicMock for the catools
        class and assign our return function to the caget method on our catools.
        Next we create a blank cothread module and then put our catools class
        into it. Finally, we edit sys.modules to ensure our new mocked code is
        called in the place of the original.
    """
    def return_func(pvs, timeout, throw):
        if type(pvs) is list:
            return [DUMMY_VALUE_1, DUMMY_VALUE_2]
        else:
            return DUMMY_VALUE_1

    catools = MagicMock()
    catools.caget = return_func
    cothread = ModuleType('cothread')
    cothread.catools = catools
    sys.modules['cothread'] = cothread
    sys.modules['cothread.catools'] = catools
    # Caproto
    """Travis also can't import caproto, but more importantly caproto requires a
        python version of 3.6 or greater. So in order to make sure the tests
        always run correctly we must mock caproto. N.B. this is significantly
        more complicated than mocking cothread as the process of getting values
        from PVs is significantly more complex in caproto.
       First we create a fixture that returns our response object, with the data
        as an attribute, in the correct manner. Next we create a new mock client
        class with sub-classes Context and Batch, these sub-classes have the
        correct methods and logic to return the right values in the appropriate
        way to emulate caproto as we use it. Then we create the blank modules,
        caproto and caproto.threading, and put our client class inside the
        latter. Finally we edit sys.modules to ensure that our mocked caproto
        code is called instead of the original.
    """
    @pytest.fixture(scope='session')
    def r(values):
        class response(object):
            def __init__(self, values):
                self.data = [values]
        res = response(values)
        return res

    class client(object):
        class Context(object):
            def get_pvs(self, *pvs):
                if len(pvs) > 1:
                    pv_obj_1 = MagicMock()
                    pv_obj_1.read.return_value = r(DUMMY_VALUE_1)
                    pv_obj_2 = MagicMock()
                    pv_obj_2.read.return_value = r(DUMMY_VALUE_2)
                    return [pv_obj_1, pv_obj_2]
                else:
                    pv_obj = MagicMock()
                    pv_obj.read.return_value = r(DUMMY_VALUE_1)
                    return [pv_obj]

        class Batch(object):
            def __enter__(self):
                return self

            def read(self, pv_obj, callback):
                callback(pv_obj.read())

            def write(self, pv_obj, value):
                pass

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

    caproto = ModuleType('caproto')
    caproto.threading = ModuleType('caproto.threading')
    caproto.threading.client = client
    sys.modules['caproto'] = caproto
    sys.modules['caproto.threading'] = caproto.threading
    sys.modules['caproto.threading.client'] = client


@pytest.fixture(scope="session")
def mock_cs_raises_ImportError():
    """We create a mock control system to replace CothreadControlSystem, so that
        we can check that when it raises an ImportError load_csv.load catches it
        and raises a LatticeException instead.
       N.B. Our new CothreadControlSystem is nested inside a fixture so it can
        be patched into pytac.cothread_cs to replace the existing
        CothreadControlSystem class. The new CothreadControlSystem created here
        is a function not a class (like the original) to prevent it from raising
        the ImportError when the code is compiled.
    """
    def CothreadControlSystem():
        raise ImportError
    return CothreadControlSystem


@pytest.fixture(scope='session')
def make_control_system(cs):
    """This function depending upon it's input creates either a cothread or
        caproto control system and returns it. This is used to enable the use of
        parametrization in tests that are not control system specific.
    """
    if cs == 'cothread':
        from pytac import cothread_cs
        return cothread_cs.CothreadControlSystem()
    elif cs == 'caproto':
        from pytac import caproto_cs
        return caproto_cs.CaprotoControlSystem()


def test_import_caproto_cs(Travis_CI_compatibility):
    """Test that the caproto control system sucessfully loads.
    """
    cs = make_control_system('caproto')
    assert bool(load('VMX', cs))


def test_default_control_system_import(Travis_CI_compatibility):
    """In this test we:
        - assert that the lattice is indeed loaded if no execeptions are raised.
        - assert that the default control system is indeed cothread and that it
           is loaded onto the lattice correctly.
    """
    assert bool(load('VMX'))
    assert isinstance(load('VMX')._cs, pytac.cothread_cs.CothreadControlSystem)


def test_import_fail_raises_LatticeException(Travis_CI_compatibility,
                                             mock_cs_raises_ImportError):
    """In this test we:
        - check that load corectly fails if cothread cannot be imported.
        - check that when the import of the CothreadControlSystem fails the
           ImportError raised is replaced with a LatticeException.
    """
    with patch('pytac.cothread_cs.CothreadControlSystem',
               mock_cs_raises_ImportError):
        with pytest.raises(LatticeException):
            load('VMX')


@pytest.mark.parametrize('cs', ['cothread', 'caproto'])
def test_control_system_raises_ValueError(Travis_CI_compatibility, cs):
    """Test that all the control systems raise errors correctly.
    """
    control_system = make_control_system(cs)
    with pytest.raises(ValueError):
        control_system.get_multiple('not_a_list')
    with pytest.raises(ValueError):
        control_system.set_multiple('not_a_list', [DUMMY_VALUE_1])
    with pytest.raises(ValueError):
        control_system.set_multiple(['pv_1'], [])
    with pytest.raises(ValueError):
        control_system.set_multiple(['pv_1'], [DUMMY_VALUE_1, DUMMY_VALUE_2])


@pytest.mark.parametrize('cs', ['cothread', 'caproto'])
def test_cothread_control_system_methods(Travis_CI_compatibility, cs):
    """Test that all control systems call all of their methods correctly.
    """
    control_system = make_control_system(cs)
    assert control_system.get_single('pv_1') == DUMMY_VALUE_1
    assert control_system.get_multiple(['pv_1', 'pv_2']) == [DUMMY_VALUE_1,
                                                             DUMMY_VALUE_2]
    control_system.set_single('pv_1', DUMMY_VALUE_1)
    control_system.set_multiple(['pv_1', 'pv_2'], [DUMMY_VALUE_1,
                                                   DUMMY_VALUE_2])


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
