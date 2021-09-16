"""The device class used to represent a particular function of an accelerator
element.

A physical element in an accelerator may have multiple devices: an example at
DLS is a sextupole magnet that contains also horizontal and vertical corrector
magnets and a skew quadrupole.
"""
from typing import List, Union

import pytac
from pytac.exceptions import DataSourceException, HandleException


class Device:
    """A representation of a property of an element associated with a field.

    Typically a control system will be used to set and get values on a
    device.

    **Methods:**
    """

    def is_enabled(self) -> bool:
        """Whether the device is enabled.

        Returns:
            whether the device is enabled.
        """
        raise NotImplementedError()

    def get_value(self, handle: str, throw: bool) -> float:
        """Read the value from the device.

        Args:
            handle: pytac.SP or pytac.RB.
            throw: On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            the value of the PV.
        """
        raise NotImplementedError()

    def set_value(self, value: float, throw: bool) -> None:
        """Set the value on the device.

        Args:
            value (float): the value to set.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.
        """
        raise NotImplementedError()


class SimpleDevice(Device):
    """A basic implementation of the device class.

    This device does not have a PV associated with it, nor does it interact
    with a simulator. In short this device acts as simple storage for data
    that rarely changes, as it is not affected by changes to other aspects of
    the accelerator.
    """

    def __init__(
        self,
        value: Union[float, List[float]],
        enabled: bool = True,
        readonly: bool = True,
    ):
        """
        Args:
            value: can be a number or a list of numbers.
            enabled: whether the device is enabled. May be a
                                  PvEnabler object.
            readonly: whether the value may be changed.
        """
        self._value = value
        self._enabled = enabled
        self._readonly = readonly

    def is_enabled(self):
        """Whether the device is enabled.

        Returns:
            bool: whether the device is enabled.
        """
        return bool(self._enabled)

    def get_value(self, handle=None, throw=None):
        """Read the value from the device.

        Args:
            handle (str): Irrelevant in this case as a control system is not
                           used, only supported to conform with the base class.
            throw (bool): Irrelevant in this case as a control system is not
                           used, only supported to conform with the base class.

        Returns:
            numeric: the value of the device.
        """
        return self._value

    def set_value(self, value, throw=None):
        """Set the value on the device.

        Args:
            value (numeric): the value to set.
            throw (bool): Irrelevant in this case as a control system is not
                           used, only supported to conform with the base class.
        """
        if self._readonly:
            raise ValueError("Cannot change value of readonly SimpleDevice")
        self.value = value


class EpicsDevice(Device):
    """An EPICS-aware device.

    Contains a control system, readback and setpoint PVs. A readback or
    setpoint PV is required when creating an epics device otherwise a
    DataSourceException is raised. The device is enabled by default.

    **Attributes:**

    Attributes:
        name (str): The prefix of EPICS PVs for this device.
        rb_pv (str): The EPICS readback PV.
        sp_pv (str): The EPICS setpoint PV.

    .. Private Attributes:
           _cs (ControlSystem): The control system object used to get and set
                                 the value of a PV.
           _enabled (bool-like): Whether the device is enabled. May be a
                                  PvEnabler object.
    """

    def __init__(self, name, cs, enabled=True, rb_pv=None, sp_pv=None):
        """
        Args:
            name (str): The prefix of EPICS PV for this device.
            cs (ControlSystem): The control system object used to get and set
                                 the value of a PV.
            enabled (bool-like): Whether the device is enabled. May be a
                                  PvEnabler object.
            rb_pv (str): The EPICS readback PV.
            sp_pv (str): The EPICS setpoint PV.

        Raises:
            DataSourceException: if no PVs are provided.

        **Methods:**
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

    def is_enabled(self):
        """Whether the device is enabled.

        Returns:
            bool: whether the device is enabled.
        """
        return bool(self._enabled)

    def get_value(self, handle, throw=True):
        """Read the value of a readback or setpoint PV.

        Args:
            handle (str): pytac.SP or pytac.RB.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            float: The value of the PV.

        Raises:
            HandleException: if the requested PV doesn't exist.
        """
        return self._cs.get_single(self.get_pv_name(handle), throw)

    def set_value(self, value, throw=True):
        """Set the device value.

        Args:
            value (float): The value to set.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.

        Raises:
            HandleException: if no setpoint PV exists.
        """
        self._cs.set_single(self.get_pv_name(pytac.SP), value, throw)

    def get_pv_name(self, handle):
        """Get the PV name for the specified handle.

        Args:
            handle (str): The readback or setpoint handle to be returned.

        Returns:
            str: A readback or setpoint PV.

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

    .. Private Attributes:
           _pv (str): The PV name.
           _enabled_value (str): The value for PV for which the device should
                                  be considered enabled.
           _cs (ControlSystem): The control system object.
    """

    def __init__(self, pv, enabled_value, cs):
        """
        Args:
            pv (str): The PV name.
            enabled_value (str): The value for PV for which the device should
                                  be considered enabled.
            cs (ControlSystem): The control system object.

        **Methods:**
        """
        self._pv = pv
        self._enabled_value = str(int(float(enabled_value)))
        self._cs = cs

    def __bool__(self):
        """Used to override the 'if object' clause.

        Returns:
            bool: True if the device should be considered enabled.
        """
        pv_value = self._cs.get_single(self._pv)
        return self._enabled_value == str(int(float(pv_value)))
