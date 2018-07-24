"""The device class used to represent a particular function of an accelerator element.

A physical element in an accelerator may have multiple devices: an example at DLS
is a sextupole magnet that contains also horizontal and vertical corrector magnets
and a skew quadrupole.
"""
import pytac


class DeviceException(Exception):
    """Exception associated with Device misconfiguration or invalid requests."""
    pass


class Device(object):
    """A device attached to an element.

    Contains a control system, readback and setpoint pvs. A readback
    or setpoint pv is required when creating a device otherwise a
    DeviceException is raised. The device is enabled by default.

    **Attributes:**

    Attributes:
        name (str): The prefix of EPICS pvs for this device.
        rb_pv (str): The EPICS readback pv.
        sp_pv (str): The EPICS setpoint pv.

    .. Private Attributes:
           _cs (ControlSystem): The control system object used to get and set
                                 the value of a pv.
           _enabled (bool-like): Whether the device is enabled. May be a
                                  PvEnabler object.
    """

    def __init__(self, name, cs, enabled=True, rb_pv=None, sp_pv=None):
        """
        Args:
            name (str): The prefix of EPICS pvs for this device.
            cs (ControlSystem): The control system object used to get and set
                                 the value of a pv.
            enabled (bool-like): Whether the device is enabled. May be a
                                  PvEnabler object.
            rb_suffix (str): The EPICS readback pv.
            sp_suffix (str): The EPICS setpoint pv.
        """
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

    def set_value(self, value):
        """Set the device value.

        Args:
            value (float): The value to set on the pv.

        Raises:
            DeviceException: if no setpoint pv exists.
        """
        if self.sp_pv is None:
            raise DeviceException("""Device {0} has no setpoint pv."""
                              .format(self.name))
        self._cs.put(self.sp_pv, value)

    def get_value(self, handle):
        """Read the value of a readback or setpoint pv.

        Args:
            handle (str): The handle used to get the value off a readback or
                           setpoint pv.

        Returns:
            float: The value of the pv.

        Raises:
            DeviceException: if the requested pv doesn't exist.
        """
        print('getting {}'.format('handle'))
        if handle == pytac.RB and self.rb_pv:
            return self._cs.get(self.rb_pv)
        elif handle == pytac.SP and self.sp_pv:
            return self._cs.get(self.sp_pv)

        raise DeviceException("""Device {0} has no {1} pv."""
                          .format(self.name, handle))

    def get_pv_name(self, handle):
        """Get a pv name on a specified handle.

        Args:
            handle (str): The readback or setpoint handle to be returned.

        Returns:
            str: A readback or setpoint pv.

        Raises:
            DeviceException: if the pv doesn't exist.
        """
        if handle == pytac.RB and self.rb_pv:
            return self.rb_pv
        elif handle == pytac.SP and self.sp_pv:
            return self.sp_pv

        raise DeviceException("""Device {0} has no {1} pv."""
                          .format(self.name, handle))

    def get_cs(self):
        """The control system object used to get and set the value of a pv.

        Returns:
            ControlSystem: The control system object used to get and set the
            value of a pv.
        """
        return self._cs


class PvEnabler(object):
    def __init__(self, pv, enabled_value, cs):
        """A PvEnabler class to check whether a device is enabled.

        The class will behave like True if the pv value equals enabled_value,
        and False otherwise.

        Args:
            pv (str): The pv name.
            enabled_value (str): The value for pv for which the device should
                be considered enabled.
            cs (ControlSystem): The control system object.
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
        pv_value = self._cs.get(self._pv)
        return self._enabled_value == str(int(float(pv_value)))

    def __bool__(self):
        """Used to override the 'if object' clause.

        Support for Python 3.x.

        Returns:
            bool: True if the device should be considered enabled.
        """
        return self.__nonzero__()
