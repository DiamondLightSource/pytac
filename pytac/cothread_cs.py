import logging

from cothread.catools import caget, caput, ca_nothing

from pytac.cs import ControlSystem
from pytac.exceptions import ControlSystemException


class CothreadControlSystem(ControlSystem):
    """A control system using cothread to communicate with EPICS.

    N.B. this is the default control system. It is used to communicate over
    channel access with the hardware in the ring.

    **Methods:**
    """

    def __init__(self, timeout=1.0):
        self._timeout = timeout

    def get_single(self, pv, throw=True):
        """Get the value of a given PV.

        Args:
            pv (string): The process variable given as a string. It can be a
                         readback or a setpoint PV.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            object: the current value of the given PV.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        try:
            return caget(pv, timeout=self._timeout, throw=True)
        except ca_nothing:
            error_msg = f"Cannot connect to {pv}."
            if throw:
                raise ControlSystemException(error_msg)
            else:
                logging.warning(error_msg)
                return None

    def get_multiple(self, pvs, throw=True):
        """Get the value for given PVs.

        Args:
            pvs (sequence): PVs to get values of.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, None will be returned for any PV that fails
                           and a warning will be logged.

        Returns:
            sequence: the current values of the PVs.

        Raises:
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        results = caget(pvs, timeout=self._timeout, throw=False)
        return_values = []
        failures = []
        for result in results:
            if isinstance(result, ca_nothing):
                logging.warning(f"Cannot connect to {result.name}.")
                if throw:
                    failures.append(result)
                else:
                    return_values.append(None)
            else:
                return_values.append(result)
        if throw and failures:
            raise ControlSystemException(f"{len(failures)} caget calls failed.")
        return return_values

    def set_single(self, pv, value, throw=True):
        """Set the value of a given PV.

        Args:
            pv (string): PV to set the value of.
            value (object): The value to set the PV to.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.

        Returns:
            bool: True for success, False for failure

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        try:
            caput(pv, value, timeout=self._timeout, throw=True)
            return True
        except ca_nothing:
            error_msg = f"Cannot connect to {pv}."
            if throw:
                raise ControlSystemException(error_msg)
            else:
                logging.warning(error_msg)
                return False

    def set_multiple(self, pvs, values, throw=True):
        """Set the values for given PVs.

        Args:
            pvs (sequence): PVs to set the values of.
            values (sequence): values to set to the PVs.
            throw (bool): On failure, if True raise ControlSystemException, if
                           False return a list of True and False values
                           corresponding to successes and failures and log a
                           warning for each PV that fails.

        Returns:
            list(bool): True for success, False for failure; only returned if
                         throw is false and a failure occurs.

        Raises:
            ValueError: if the lists of values and PVs are diffent lengths.
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        if len(pvs) != len(values):
            raise ValueError("Please enter the same number of values as PVs.")
        status = caput(pvs, values, timeout=self._timeout, throw=False)
        return_values = []
        failures = []
        for stat in status:
            if not stat.ok:
                return_values.append(False)
                failures.append(stat)
                logging.warning(f"Cannot connect to {stat.name}.")
            else:
                return_values.append(True)
        if failures:
            if throw:
                raise ControlSystemException(f"{len(failures)} caput calls failed.")
            else:
                return return_values
