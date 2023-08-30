"""Class representing an abstract control system."""


from typing import (
    List,
    Optional,
    Sequence,
    Sized,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
)


class AugmentedType(SupportsFloat, SupportsInt, SupportsIndex, Sized):
    pass


class ControlSystem(object):
    """Abstract base class representing a control system.

    A specialised implementation of this class would be used to communicate
    over channel access with the hardware in the ring.
    """

    def get_single(self, pv: str, throw: bool) -> Optional[AugmentedType]:
        """Get the value of a given PV.

        Args:
            pv: PV to get the value of readback or a setpoint PV.
            throw: On failure: if True, raise ControlSystemException; if False,
                return None and log a warning.

        Returns:
            The current value of the given PV.

        Raises:
            ControlSystemException: if it cannot connect to the specified PVs.
        """
        raise NotImplementedError()

    def get_multiple(
        self, pvs: Sequence[str], throw: bool
    ) -> List[Optional[AugmentedType]]:
        """Get the value for given PVs.

        Args:
            pvs: PVs to get values of.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            The current values of the PVs.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        raise NotImplementedError()

    def set_single(self, pv: str, value: AugmentedType, throw: bool) -> bool:
        """Set the value of a given PV.

        Args:
            pv: The PV to set the value of.
            value: The value to set the PV to.
            throw: On failure: if True, raise ControlSystemException: if False,
                log a warning.

        Raises:
            ControlSystemException: if it cannot connect to the specified PV.
        """
        raise NotImplementedError()

    def set_multiple(
        self, pvs: Sequence[str], values: Sequence[AugmentedType], throw: bool
    ) -> Optional[List[bool]]:
        """Set the values for given PVs.

        Args:
            pvs: PVs to set the values of.
            values: values to set no the PVs.
            throw: On failure, if True raise ControlSystemException, if False return a
                list of True and False values corresponding to successes and failures
                and log a warning for each PV that fails.

        Raises:
            ValueError: if the PVs or values are not passed in as sequences or if they
                have different lengths
            ControlSystemException: if it cannot connect to one or more PVs.
        """
        raise NotImplementedError()
