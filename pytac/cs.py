"""
Template module to define control systems.
"""


class ControlSystem(object):
    """ Define a control system to be used with a device.

    It uses channel access to comunicate over the network with
    the hardware.
    """
    def __init__(self):
        raise NotImplementedError()

    def get(self, pv):
        """ Get the value of the given pv.

        Args:
            pv(string): The Pv to get the value of.

        Returns:
            Number: The numeric value of the pv.
        """
        raise NotImplementedError()

    def put(self, pv, value):
        """ Put the value of a given pv.

        Args:
            pv(string): The string to put the value for.
            value(Number): The value to be set.
        """
        raise NotImplementedError()
