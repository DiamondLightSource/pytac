"""Tests for the AIOCAControlSystem class."""

from unittest.mock import MagicMock, patch

import pytest
from constants import RB_PV, SP_PV
from testfixtures import LogCapture

import pytac
from pytac.aioca_cs import AIOCAControlSystem


<<<<<<< Updated upstream
class CANothing(Exception):
    """A minimal mock of the cothread CANothing exception class."""
=======
class CANothing(Exception):  # noqa: N818
    """A minimal mock of the aioca CANothing exception class."""
>>>>>>> Stashed changes

    def __init__(self, name, errorcode=True):
        self.ok = errorcode
        self.name = name


@pytest.fixture
def cs():
    return AIOCAControlSystem(wait=True, timeout=2.0)


@patch("pytac.aioca_cs.caget")
async def test_get_single_calls_caget_correctly(caget: MagicMock, cs):
    caget.return_value = 42
    assert (await cs.get_single(RB_PV)) == 42
    caget.assert_called_with(RB_PV, throw=True, timeout=2.0)


@patch("pytac.aioca_cs.caget")
async def test_get_multiple_calls_caget_correctly(caget: MagicMock, cs):
    """caget is called with throw=False despite throw=True being the default
    for get_multiple as we always want our get operation to fully complete,
    rather than being stopped halway through by an error raised from
    aioca, so that even if one get operation to a PV fails the rest will
    complete sucessfully.
    """
    caget.return_value = [42, 6]
    assert await cs.get_multiple([RB_PV, SP_PV]) == [42, 6]
    caget.assert_called_with([RB_PV, SP_PV], throw=False, timeout=2.0)


@patch("pytac.aioca_cs.caput")
async def test_set_single_calls_caput_correctly(caput: MagicMock, cs):
    assert await cs.set_single(SP_PV, 42) is True
    caput.assert_called_with(SP_PV, 42, throw=True, timeout=2.0, wait=True)


@patch("pytac.aioca_cs.caput")
async def test_set_multiple_calls_caput_correctly(caput: MagicMock, cs):
    """caput is called with throw=False despite throw=True being the default
    for set_multiple as we always want our set operation to fully complete,
    rather than being stopped halway through by an error raised from
    aioca, so that even if one set operation to a PV fails the rest will
    complete sucessfully.
    """
    await cs.set_multiple([SP_PV, RB_PV], [42, 6])
    caput.assert_called_with(
        [SP_PV, RB_PV], [42, 6], throw=False, timeout=2.0, wait=True
    )


@patch("pytac.aioca_cs.caget")
@patch("pytac.aioca_cs.CANothing", CANothing)
async def test_get_multiple_raises_ControlSystemException(caget: MagicMock, cs):
    """Here we check that errors are thrown, suppressed and logged correctly."""
    caget.return_value = [12, CANothing("pv", False)]
    with pytest.raises(pytac.exceptions.ControlSystemException):
        await cs.get_multiple([RB_PV, SP_PV])
    with LogCapture() as log:
        assert await cs.get_multiple([RB_PV, SP_PV], throw=False) == [12, None]
    log.check(("root", "WARNING", "Cannot connect to pv."))


@patch("pytac.aioca_cs.caput")
@patch("pytac.aioca_cs.CANothing", CANothing)
async def test_set_multiple_raises_ControlSystemException(caput: MagicMock, cs):
    """Here we check that errors are thrown, suppressed and logged correctly."""
    caput.return_value = [CANothing("pv1", True), CANothing("pv2", False)]
    with pytest.raises(pytac.exceptions.ControlSystemException):
        await cs.set_multiple([RB_PV, SP_PV], [42, 6])
    with LogCapture() as log:
        assert await cs.set_multiple([RB_PV, SP_PV], [42, 6], throw=False) == [
            True,
            False,
        ]
    log.check(("root", "WARNING", "Cannot connect to pv2."))


@patch("pytac.aioca_cs.caget")
@patch("pytac.aioca_cs.CANothing", CANothing)
async def test_get_single_raises_ControlSystemException(caget: MagicMock, cs):
    """Here we check that errors are thrown, suppressed and logged correctly."""
    caget.side_effect = CANothing("pv", False)
    with LogCapture() as log:
        assert await cs.get_single(RB_PV, throw=False) is None
        with pytest.raises(pytac.exceptions.ControlSystemException):
            await cs.get_single(RB_PV, throw=True)
    log.check(("root", "WARNING", "Cannot connect to prefix:rb."))


@patch("pytac.aioca_cs.caput")
@patch("pytac.aioca_cs.CANothing", CANothing)
async def test_set_single_raises_ControlSystemException(caput: MagicMock, cs):
    """Here we check that errors are thrown, suppressed and logged correctly."""
    caput.side_effect = CANothing("pv", False)
    with LogCapture() as log:
        assert await cs.set_single(SP_PV, 42, throw=False) is False
        with pytest.raises(pytac.exceptions.ControlSystemException):
            await cs.set_single(SP_PV, 42, throw=True)
    log.check(("root", "WARNING", "Cannot connect to prefix:sp."))


async def test_set_multiple_raises_ValueError_on_input_length_mismatch(cs):
    with pytest.raises(ValueError):
        await cs.set_multiple([SP_PV], [42, 6])
    with pytest.raises(ValueError):
        await cs.set_multiple([SP_PV, RB_PV], [42])
