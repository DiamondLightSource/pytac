"""Tests for the CothreadControlSystem class.

This module depends on the cothread module being mocked.

See conftest.py for more.
"""
from cothread import catools
import pytest
from pytac.cothread_cs import CothreadControlSystem


@pytest.fixture
def cs():
    return CothreadControlSystem()


def test_get_single_calls_caget(cs):
    cs.get('abc')
    catools.caget.assert_called_with('abc')
