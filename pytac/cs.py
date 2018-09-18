"""Class representing an abstract control system."""


class ControlSystem(object):
    """ Abstract base class representing a control system.

    **Methods:**
    """
    def get(self, pv):
        """ Get the value of the given PV.

        Args:
            pv (string): The PV to get the value of.

        Returns:
            Number: The numeric value of the PV.
        """
        raise NotImplementedError()

    def put(self, pv, value):
        """ Put the value of a given PV.

        Args:
            pv (string): The PV to put the value for.
            value (Number): The value to be set.
        """
        raise NotImplementedError()
