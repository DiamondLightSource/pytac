"""Module to implement an EpicsControlSystem object which is used to get
    real-time data from the machine.
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
        """ Get the value of a given PV.

        Args:
            pv (string): The process variable given as a string. It can be a
                         readback or a setpoint PV.

        Returns:
            float: Represents the current value of the given PV.
        """
        return caget(pv)

    def put(self, pv, value):
        """ Set the value for a given.

        Args:
            pv (string): The PV to set the value of. It must be a setpoint PV.
            value (Number): The value to set the PV to.
        """
        caput(pv, value)
