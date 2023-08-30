"""The device class used to represent a particular function of an accelerator
element.

A physical element in an accelerator may have multiple devices: an example at
DLS is a sextupole magnet that contains also horizontal and vertical corrector
magnets and a skew quadrupole.
"""
from typing import List, Optional, Union, cast

import pytac
from pytac.cs import AugmentedType, ControlSystem
from pytac.exceptions import DataSourceException, HandleException


class Device:
    """A representation of a property of an element associated with a field.

    Typically a control system will be used to set and get values on a
    device.
    """

    def is_enabled(self) -> bool:
        """Whether the device is enabled.

        Returns:
            whether the device is enabled.
        """
        raise NotImplementedError()

    def get_value(self, handle: Optional[str], throw: bool) -> Optional[AugmentedType]:
        """Read the value from the device.

        Args:
            handle: pytac.SP or pytac.RB.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            the value of the PV.
        """
        raise NotImplementedError()

    def set_value(self, value: AugmentedType, throw: bool) -> None:
        """Set the value on the device.

        Args:
            value: the value to set.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.
        """
        raise NotImplementedError()


class SimpleDevice(Device):
    """A basic implementation of the device class.

    This device does not have a PV associated with it, nor does it interact
    with a simulator. In short this device acts as simple storage for data
    that rarely changes, as it is not affected by changes to other aspects of
    the accelerator.
    """

    _value: Optional[AugmentedType]
    """The value of the device. May be a number or list of numbers."""
    _enabled: Union[bool, "PvEnabler"]
    """Whether the device is enabled. May be a PvEnabler Object."""
    _readonly: bool
    """Whether the value may be changed."""

    def __init__(
        self,
        value: Optional[AugmentedType],
        enabled: Union[bool, "PvEnabler"] = True,
        readonly: bool = True,
    ) -> None:
        """Initialise the SimpleDevice object.

        Args:
            value: The value of the device. May be a number or list of numbers.
            enabled: Whether the device is enabled. May be a PvEnabler Object.
            readonly: Whether the value may be changed.
        """
        self._value = value
        self._enabled = enabled
        self._readonly = readonly

    def is_enabled(self) -> bool:
        """Whether the device is enabled.

        Returns:
            Whether the device is enabled.
        """
        return bool(self._enabled)

    def get_value(
        self, handle: Optional[str] = None, throw: Optional[bool] = None
    ) -> Optional[AugmentedType]:
        """Read the value from the device.

        Args:
            handle: Irrelevant in this case as a control system is not used, only
                supported to conform with the base class.
            throw: Irrelevant in this case as a control system is not used, only
                supported to conform with the base class.

        Returns:
            The value of the device.
        """
        return self._value

    def set_value(
        self,
        value: Optional[AugmentedType],
        throw: Optional[bool] = None,
    ) -> None:
        """Set the value on the device.

        Args:
            value: the value to set.
            throw: Irrelevant in this case as a control system is not used, only
                supported to conform with the base class.
        """
        if self._readonly:
            raise DataSourceException("Cannot change value of readonly SimpleDevice")
        self.value = value


class EpicsDevice(Device):
    """An EPICS-aware device.

    Contains a control system, readback and setpoint PVs. A readback or
    setpoint PV is required when creating an epics device otherwise a
    DataSourceException is raised. The device is enabled by default.
    """

    name: str
    """The prefix of EPICS PVs for this device."""
    rb_pv: Optional[str]
    """The EPICS readback PV."""
    sp_pv: Optional[str]
    """The EPICS setpoint PV."""

    _cs: ControlSystem
    """The control system object used to get and set the value of a PV."""
    _enabled: Union[bool, "PvEnabler"]
    """Whether the device is enabled. May be a PvEnabler object."""

    def __init__(
        self,
        name: str,
        cs: ControlSystem,
        enabled: Union[bool, "PvEnabler"] = True,
        rb_pv: Optional[str] = None,
        sp_pv: Optional[str] = None,
    ) -> None:
        """
        Args:
            name: The prefix of EPICS PV for this device.
            cs: The control system object used to get and set the value of a PV.
            enabled: Whether the device is enabled. May be a PvEnabler object.
            rb_pv: The EPICS readback PV.
            sp_pv: The EPICS setpoint PV.

        Raises:
            DataSourceException: if no PVs are provided.
        """
        if rb_pv is None and sp_pv is None:
            raise DataSourceException(
                f"At least one PV ({pytac.RB} or {pytac.SP}) is "
                "required when creating an EpicsDevice."
            )
        self.name = name
        self._cs = cs
        self.rb_pv = rb_pv
        self.sp_pv = sp_pv
        self._enabled = enabled

    def is_enabled(self) -> bool:
        """Whether the device is enabled.

        Returns:
            Whether the device is enabled.
        """
        return bool(self._enabled)

    def get_value(
        self, handle: Optional[str], throw: bool = True
    ) -> Optional[AugmentedType]:
        """Read the value of a readback or setpoint PV.

        Args:
            handle: pytac.SP or pytac.RB.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            The value of the PV.

        Raises:
            HandleException: if the requested PV doesn't exist.
        """
        return self._cs.get_single(self.get_pv_name(handle), throw)

    def set_value(self, value: AugmentedType, throw: bool = True) -> None:
        """Set the device value.

        Args:
            value: The value to set.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Raises:
            HandleException: if no setpoint PV exists.
        """
        self._cs.set_single(self.get_pv_name(pytac.SP), value, throw)

    def get_pv_name(self, handle: Optional[str]) -> str:
        """Get the PV name for the specified handle.

        Args:
            handle: The readback or setpoint handle to be returned.

        Returns:
            A readback or setpoint PV.

        Raises:
            HandleException: if the PV doesn't exist.
        """
        if handle == pytac.RB and self.rb_pv:
            return self.rb_pv
        elif handle == pytac.SP and self.sp_pv:
            return self.sp_pv
        else:
            raise HandleException(f"Device {self.name} has no {handle} PV.")


class PvEnabler(object):
    """A PvEnabler class to check whether a device is enabled.

    The class will behave like True if the PV value equals enabled_value,
    and False otherwise.
    """

    _pv: str
    """The PV name."""
    _enabled_value: str
    """The value for PV for which the device should be considered enabled."""
    _cs: ControlSystem
    """The control system object."""

    def __init__(self, pv: str, enabled_value: str, cs: ControlSystem) -> None:
        """
        Args:
            pv: The PV name.
            enabled_value: The value for PV for which the device should be
                considered enabled.
            cs: The control system object.
        """
        self._pv = pv
        self._enabled_value = str(int(float(enabled_value)))
        self._cs = cs

    def __bool__(self) -> bool:
        """Used to override the 'if object' clause.

        Returns:
            True if the device should be considered enabled.
        """
        pv_value = self._cs.get_single(self._pv, throw=True)
        # pv_value is not None as throw is True.
        # This would raise a ControlSystemException rather than returning None.
        pv_value_cast = cast(AugmentedType, pv_value)
        return self._enabled_value == str(int(float(pv_value_cast)))
