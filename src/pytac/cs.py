"""Class representing an abstract control system."""


class ControlSystem(object):
    """Abstract base class representing a control system.

    A specialised implementation of this class would be used to communicate
    over channel access with the hardware in the ring.

    **Methods:**
    """

    def get_single(self, pv, throw):
        """Get the value of a given PV.

        Args:
            pv (str): PV to get the value of.
                         readback or a setpoint PV.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            object: the current value of the given PV.

        Raises:
            ControlSystemException: if it cannot connect to the specified PVs.
        """
        raise NotImplementedError()

    def get_multiple(self, pvs, throw):
        """Get the value for given PVs.

        Args:
            pvs (typing.Sequence): PVs to get values of.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, None will be returned for any PV that fails
                           and a warning will be logged.

        Returns:
            list(object): the current values of the PVs.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        raise NotImplementedError()

    def set_single(self, pv, value, throw):
        """Set the value of a given PV.

        Args:
            pv (str): The PV to set the value of.
            value (object): The value to set the PV to.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        raise NotImplementedError()

    def set_multiple(self, pvs, values, throw):
        """Set the values for given PVs.

        Args:
            pvs (typing.Sequence): PVs to set the values of.
            values (typing.Sequence): values to set no the PVs.
            throw (bool): On failure, if True raise ControlSystemException, if
                           False return a list of True and False values
                           corresponding to successes and failures and log a
                           warning for each PV that fails.

        Raises:
            ValueError: if the PVs or values are not passed in as sequences
                        or if they have different lengths
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        raise NotImplementedError()
