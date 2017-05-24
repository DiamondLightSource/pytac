"""
Class to implement an EpicsControlSystem object which is used to
get real-time data from the synchrotron.
"""

from pytac.cs import ControlSystem
from cothread.catools import caget, caput


class EpicsControlSystem(ControlSystem):
    """ The EPICS control system.

    It is used to communicate over channel access with the hardware
    in the ring.
    """
    def __init__(self):
        pass

    def get(self, pv):
        """ Get the value of a given pv.

        Args:
            pv(string): The process variable given as a string. It can be
                a readback or a setpoint pv.

        Returns:
            float: Represents the current value of the given pv.
        """
        return caget(pv)

    def put(self, pv, value):
        """ Set the value for a given.

        Args:
            pv(string): The pv to set the value of. It must be a setpoint pv.
            value(Number): The value to set the pv to.
        """
        caput(pv, value)
