import pytest
from pytac import cs


class InvalidControlSystem(cs.ControlSystem):
    """
    Extends ControlSystem without implementing required methods.
    """
    def __init__(self):
        pass


def test_ControlSystem_throws_NotImplememtedError():
    with pytest.raises(NotImplementedError):
        cs.ControlSystem()


def test_InvalidControlSystem_throws_NotImplementedError():
    ics = InvalidControlSystem()
    with pytest.raises(NotImplementedError):
        ics.get('dummy')
    with pytest.raises(NotImplementedError):
        ics.put('dummy', 1)
