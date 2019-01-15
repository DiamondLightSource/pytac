"""Tests for the CothreadControlSystem class.

This module depends on the cothread module being mocked.

See pytest_sessionstart() in conftest.py for more.
"""
import pytac
import pytest
from constants import RB_PV, SP_PV
from testfixtures import LogCapture
from cothread.catools import caget, caput, ca_nothing
from pytac.cothread_cs import CothreadControlSystem


@pytest.fixture
def cs():
    return CothreadControlSystem()


def test_get_single_calls_caget_correctly(cs):
    caget.return_value = 42
    assert cs.get_single(RB_PV) is 42
    caget.assert_called_with(RB_PV, throw=True, timeout=1.0)


def test_get_multiple_calls_caget_correctly(cs):
    """caget is called with throw=False despite throw=True being the default
        for get_multiple as we always want our get operation to fully complete,
        rather than being stopped halway through by an error raised from
        cothread, so that even if one get operation to a PV fails the rest will
        complete sucessfully.
    """
    caget.return_value = [42, 6]
    assert cs.get_multiple([RB_PV, SP_PV]) == [42, 6]
    caget.assert_called_with([RB_PV, SP_PV], throw=False, timeout=1.0)


def test_set_single_calls_caput_correctly(cs):
    assert cs.set_single(SP_PV, 42) is True
    caput.assert_called_with(SP_PV, 42, throw=True, timeout=1.0)


def test_set_multiple_calls_caput_correctly(cs):
    """caput is called with throw=False despite throw=True being the default
        for set_multiple as we always want our set operation to fully complete,
        rather than being stopped halway through by an error raised from
        cothread, so that even if one set operation to a PV fails the rest will
        complete sucessfully.
    """
    cs.set_multiple([SP_PV, RB_PV], [42, 6])
    caput.assert_called_with([SP_PV, RB_PV], [42, 6], throw=False, timeout=1.0)


def test_get_multiple_raises_ControlSystemException(cs):
    """Here we check that errors are thrown, suppressed and logged correctly.
    """
    caget.return_value = [12, ca_nothing('pv', False)]
    with pytest.raises(pytac.exceptions.ControlSystemException):
        cs.get_multiple([RB_PV, SP_PV])
    with LogCapture() as log:
        assert cs.get_multiple([RB_PV, SP_PV], throw=False) == [12, None]
    log.check(('root', 'WARNING', 'Cannot connect to pv.'))


def test_set_multiple_raises_ControlSystemException(cs):
    """Here we check that errors are thrown, suppressed and logged correctly.
    """
    caput.return_value = [ca_nothing('pv1', True), ca_nothing('pv2', False)]
    with pytest.raises(pytac.exceptions.ControlSystemException):
        cs.set_multiple([RB_PV, SP_PV], [42, 6])
    with LogCapture() as log:
        assert cs.set_multiple([RB_PV, SP_PV], [42, 6], throw=False) == [True,
                                                                         False]
    log.check(('root', 'WARNING', 'Cannot connect to pv2.'))


def test_get_single_raises_ControlSystemException(cs):
    """Here we check that errors are thrown, suppressed and logged correctly.
    """
    caget.side_effect = ca_nothing('pv', False)
    with LogCapture() as log:
        assert cs.get_single(RB_PV, throw=False) is None
        with pytest.raises(pytac.exceptions.ControlSystemException):
            cs.get_single(RB_PV, throw=True)
    log.check(('root', 'WARNING', 'Cannot connect to prefix:rb.'))


def test_set_single_raises_ControlSystemException(cs):
    """Here we check that errors are thrown, suppressed and logged correctly.
    """
    caput.side_effect = ca_nothing('pv', False)
    with LogCapture() as log:
        assert cs.set_single(SP_PV, 42, throw=False) is False
        with pytest.raises(pytac.exceptions.ControlSystemException):
            cs.set_single(SP_PV, 42, throw=True)
    log.check(('root', 'WARNING', 'Cannot connect to prefix:sp.'))


def test_set_multiple_raises_ValueError_on_input_length_mismatch(cs):
    with pytest.raises(ValueError):
        cs.set_multiple([SP_PV], [42, 6])
    with pytest.raises(ValueError):
        cs.set_multiple([SP_PV, RB_PV], [42])
