"""The device class used to represent a particular function of an accelerator
element.

A physical element in an accelerator may have multiple devices: an example at
DLS is a sextupole magnet that contains also horizontal and vertical corrector
magnets and a skew quadrupole.
"""
import pytac
from pytac.exceptions import DataSourceException, HandleException


class Device(object):
    """A representation of a property of an element associated with a field.

    Typically a control system will be used to set and get values on a
    device.

    **Methods:**
    """
    def is_enabled(self):
        """Whether the device is enabled.

        Returns:
            bool: whether the device is enabled.
        """
        raise NotImplementedError()

    def get_value(self, handle, throw):
        """Read the value from the device.

        Args:
            handle (str): pytac.SP or pytac.RB.
            throw (bool): On failure, if True raise ControlSystemException, if
                           False None will be returned for any PV that fails
                           and log a warning.

        Returns:
            float: the value of the PV.
        """
        raise NotImplementedError()

    def set_value(self, value, throw):
        """Set the value on the device.

        Args:
            value (float): the value to set.
            throw (bool): On failure, if True raise ControlSystemException, if
                           False log a warning.
        """
        raise NotImplementedError()


class BasicDevice(Device):
    """A basic implementation of the device class. This device does not have a
        pv associated with it, nor does it interact with a simulator. In short
        this device acts as simple storage for data that rarely changes, as it
        is not affected by changes to other aspects of the accelerator.
    """
    def __init__(self, value, enabled=True):
        """Args:
            value (numeric): can be a number or a list of numbers.
            enabled (bool-like): Whether the device is enabled. May be a
                                  PvEnabler object.
        """
        self.value = value
        self._enabled = enabled

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
        return self.value

    def set_value(self, value, throw=None):
        """Set the value on the device.

        Args:
            value (numeric): the value to set.
            throw (bool): Irrelevant in this case as a control system is not
                           used, only supported to conform with the base class.
        """
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
            raise DataSourceException("At least one PV, either {0} or {1} is "
                                      "required when creating an EpicsDevice."
                                      .format(pytac.RB, pytac.SP))
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
            throw (bool): On failure, if True raise ControlSystemException, if
                           False None will be returned for any PV that fails
                           and log a warning.

        Returns:
            float: The value of the PV.

        Raises:
            HandleException: if the requested PV doesn't exist.
        """
        if handle == pytac.RB and self.rb_pv:
            return self._cs.get_single(self.rb_pv, throw)
        elif handle == pytac.SP and self.sp_pv:
            return self._cs.get_single(self.sp_pv, throw)
        else:
            raise HandleException("Device {0} has no {1} PV."
                                  .format(self.name, handle))

    def set_value(self, value, throw=True):
        """Set the device value.

        Args:
            value (float): The value to set.
            throw (bool): On failure, if True raise ControlSystemException, if
                           False log a warning.

        Raises:
            HandleException: if no setpoint PV exists.
        """
        if self.sp_pv is None:
            raise HandleException("Device {0} has no setpoint PV."
                                  .format(self.name))
        else:
            self._cs.set_single(self.sp_pv, value, throw)

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
            raise HandleException("Device {0} has no {1} PV."
                                  .format(self.name, handle))


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

    def __nonzero__(self):
        """Used to override the 'if object' clause.

        Support for Python 2.7.

        Returns:
            bool: True if the device should be considered enabled.
        """
        pv_value = self._cs.get_single(self._pv)
        return self._enabled_value == str(int(float(pv_value)))

    def __bool__(self):
        """Used to override the 'if object' clause.

        Support for Python 3.x.

        Returns:
            bool: True if the device should be considered enabled.
        """
        return self.__nonzero__()
