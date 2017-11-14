"""Class representing an abstract control system."""


class ControlSystem(object):
    """ Abstract base class representing a control system.
    """
    def __init__(self):
        raise NotImplementedError()

    def get(self, pv):
        """ Get the value of the given pv.

        Args:
            pv(string): The pv to get the value of.

        Returns:
            Number: The numeric value of the pv.
        """
        raise NotImplementedError()

    def put(self, pv, value):
        """ Put the value of a given pv.

        Args:
            pv(string): The pv to put the value for.
            value(Number): The value to be set.
        """
        raise NotImplementedError()
