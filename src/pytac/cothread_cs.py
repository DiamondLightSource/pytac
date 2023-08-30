import logging
from typing import Any, List, Optional, Sequence

from cothread.catools import ca_nothing, caget, caput

from pytac.cs import AugmentedType, ControlSystem
from pytac.exceptions import ControlSystemException


class AugmentedValue(AugmentedType):
    """A dummy class for typehinting,
    taken from aioca.aioca.types and cothread.
    """

    name: str
    """Name of the PV used to create this value."""
    ok: bool
    """True for normal data, False for error code."""


class CothreadControlSystem(ControlSystem):
    """A control system using cothread to communicate with EPICS.

    N.B. this is the default control system. It is used to communicate over
    channel access with the hardware in the ring.

    Attributes:
        _timeout: Timeout in seconds for the caget operations.
        _wait: Caput operations will wait until the server acknowledges successful
            completion before returning.
    """

    _timeout: float
    _wait: bool

    def __init__(self, timeout: float = 1.0, wait: bool = False) -> None:
        """Initialise the Cothread control system.

        Args:
            _timeout: Timeout in seconds for the caget operation.
            _wait: Caput operations will wait until the server acknowledges successful
                completion before returning.
        """
        self._timeout = timeout
        self._wait = wait

    def get_single(self, pv: str, throw: bool = True) -> Optional[AugmentedType]:
        """Get the value of a given PV.

        Args:
            pv: The process variable given as a string. It can be a readback or a
                setpoint PV.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            The current value of the given PV.

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

    def get_multiple(
        self, pvs: Sequence[str], throw: bool = True
    ) -> List[Optional[AugmentedType]]:
        """Get the value for given PVs.

        Args:
            pvs: PVs to get values of.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            The current values of the PVs.

        Raises:
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        results = caget(pvs, timeout=self._timeout, throw=False)
        return_values: List[Optional[AugmentedType]] = []
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

    def set_single(self, pv: str, value: AugmentedType, throw: bool = True) -> bool:
        """Set the value of a given PV.

        Args:
            pv: PV to set the value of.
            value: The value to set the PV to.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            True for success, False for failure

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        try:
            caput(pv, value, timeout=self._timeout, throw=True, wait=self._wait)
            return True
        except ca_nothing:
            error_msg = f"Cannot connect to {pv}."
            if throw:
                raise ControlSystemException(error_msg)
            else:
                logging.warning(error_msg)
                return False

    def set_multiple(
        self,
        pvs: Sequence[str],
        values: Sequence[AugmentedType],
        throw: bool = True,
    ) -> Optional[List[bool]]:
        """Set the values for given PVs.

        Args:
            pvs: PVs to set the values of.
            values: values to set to the PVs.
            throw: On failure, if True raise ControlSystemException, if False return
                a list of True and False values corresponding to successes and failures
                and log a warning for each PV that fails.

        Returns:
            True for success, False for failure; only returned if throw is false and a
                failure occurs.

        Raises:
            ValueError: if the lists of values and PVs are diffent lengths.
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        if len(pvs) != len(values):
            raise ValueError("Please enter the same number of values as PVs.")
        status = caput(pvs, values, timeout=self._timeout, throw=False, wait=self._wait)
        return_values: List[bool] = []
        failures: List[Any] = []
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
        return None
