from pytac.cs import ControlSystem
from pytac.exceptions import ControlSystemException
from cothread.catools import caget, caput, ca_nothing


class CothreadControlSystem(ControlSystem):
    """A control system using cothread to communicate with EPICS. N.B. this is
        the default control system.

    It is used to communicate over channel access with the hardware
    in the ring.

    **Methods:**
    """
    def __init__(self):
        pass

    def get_single(self, pv, throw=True):
        """Get the value of a given PV.

        Args:
            pv (string): The process variable given as a string. It can be a
                         readback or a setpoint PV.
            throw (bool): if True, ControlSystemException will be raised on
                          failure

        Returns:
            object: the current value of the given PV.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        try:
            return caget(pv, timeout=1.0, throw=True)
        except ca_nothing:
            if throw:
                raise ControlSystemException("Cannot connect to {0}."
                                             .format(pv))
            else:
                print('Cannot connect to {0}.'.format(pv))
                return None

    def get_multiple(self, pvs, throw=True):
        """Get the value for given PVs.

        Args:
            pvs (sequence): PVs to get values of.
            throw (bool): if True, ControlSystemException will be raised on
                          failure

        Returns:
            sequence: the current values of the PVs.

        Raises:
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        results = caget(pvs, timeout=1.0, throw=False)
        for result in results:
            if isinstance(result, ca_nothing):
                if throw:
                    raise ControlSystemException("Cannot connect to {0}."
                                                 .format(result.name))
                else:
                    print('Cannot connect to {0}.'.format(result.name))
                    result = None
        return results

    def set_single(self, pv, value, throw=True):
        """Set the value of a given PV.

        Args:
            pv (string): PV to set the value of.
            value (object): The value to set the PV to.
            throw (bool): if True, ControlSystemException will be raised on
                          failure

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        try:
            caput(pv, value, timeout=1.0, throw=True)
        except ca_nothing:
            if throw:
                raise ControlSystemException("Cannot connect to {0}."
                                             .format(pv))
            else:
                print('Cannot connect to {0}.'.format(pv))

    def set_multiple(self, pvs, values, throw=True):
        """Set the values for given PVs.

        Args:
            pvs (sequence): PVs to set the values of.
            values (sequence): values to set to the PVs.
            throw (bool): if True, ControlSystemException will be raised on
                          failure

        Returns:
            list(bool): True for success, False for failure

        Raises:
            ValueError: if the lists of values and PVs are diffent lengths.
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        if len(pvs) != len(values):
            raise ValueError("Please enter the same number of values as PVs.")
        status = caput(pvs, values, timeout=1.0, throw=False)
        for stat in status:
            if not stat.ok:
                if throw:
                    raise ControlSystemException("Cannot connect to {0}."
                                                 .format(stat.name))
                else:
                    print('Cannot connect to {0}.'.format(stat.name))
