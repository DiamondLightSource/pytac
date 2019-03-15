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
            pv (string): PV to get the value of.
                         readback or a setpoint PV.
            throw (bool): if True, ControlSystemException will be raised on
                          failure instead of warning.

        Returns:
            object: the current value of the given PV.

        Raises:
            ControlSystemException: if it cannot connect to the specified PVs.
        """
        raise NotImplementedError()

    def get_multiple(self, pvs, throw):
        """Get the value for given PVs.

        Args:
            pvs (sequence): PVs to get values of.
            throw (bool): if True, ControlSystemException will be raised on
                          failure. If False, None will be returned for any PV
                          for which the get fails.

        Returns:
            list(object): the current values of the PVs.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        raise NotImplementedError()

    def set_single(self, pv, value, throw):
        """Set the value of a given PV.

        Args:
            pv (string): The PV to set the value of.
            value (object): The value to set the PV to.
            throw (bool): if True, ControlSystemException will be raised on
                          failure instead of warning.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        raise NotImplementedError()

    def set_multiple(self, pvs, values, throw):
        """Set the values for given PVs.

        Args:
            pvs (sequence): PVs to set the values of.
            values (sequence): values to set no the PVs.
            throw (bool): if True, ControlSystemException will be raised on
                          failure. If False, a list of True and False values
                          will be returned corresponding to successes and
                          failures.

        Raises:
            ValueError: if the PVs or values are not passed in as sequences
                        or if they have different lengths
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        raise NotImplementedError()
