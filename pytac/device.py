"""The device class used to represent a particular function of an accelerator element.

A physical element in an accelerator may have multiple devices: an example at DLS
is a sextupole magnet that contains also horizontal and vertical corrector magnets
and a skew quadrupole.
"""

from pytac.exceptions import PvException
import pytac


class Device(object):
    """A device attached to an element.

    Contains a control system, readback and setpoint pvs. A readback
    or setpoint pv is required when creating a device otherwise a
    PvException is raised. The device is enabled by default.

    """

    def __init__(self, name, cs, enabled=True, rb_suffix=None, sp_suffix=None):
        """
        Args:
            name: prefix of EPICS PVs for this device
            cs (ControlSystem): Control system object used to get and set
                the value of a pv.
            enabled (bool-like): Whether the device is enabled.  May be
                a PvEnabler object.
            rb_suffix (str): suffix of EPICS readback pv
            sp_suffix (str): suffix of EPICS setpoint pv
        """
        self.name = name
        self._cs = cs
        self.rb_pv = name + rb_suffix if rb_suffix is not None else None
        self.sp_pv = name + sp_suffix if sp_suffix is not None else None
        self._enabled = enabled

    def is_enabled(self):
        """Whether the device is enabled.

        Returns:
            boolean: whether the device is enabled
        """
        return bool(self._enabled)

    def put_value(self, value):
        """Set the device value.

        Args:
            value (float): The value to set on the pv.

        Raises:
            PvException: An exception occured when no setpoint pv exists.
        """
        if self.sp_pv is None:
            raise PvException("""This device {0} has no setpoint pv."""
                              .format(self.name))
        self._cs.put(self.sp_pv, value)

    def get_value(self, handle):
        """Read the value of a readback or setpoint pv.

        If neither readback or setpoint pvs exist then a PvException is raised.

        Args:
            handle (str): Handle used to get the value off a readback or setpoint
                pv.

        Returns:
            float: The value of the pv.

        Raises:
            PvException: In case the requested pv doesn't exist.
        """
        if handle == pytac.RB and self.rb_pv:
            return self._cs.get(self.rb_pv)
        elif handle == pytac.SP and self.sp_pv:
            return self._cs.get(self.sp_pv)

        raise PvException("""This device {0} has no {1} pv."""
                          .format(self.name, handle))

    def get_pv_name(self, handle):
        """Get a pv name on a specified handle.

        Args:
            handle (str): The readback or setpoint handle to be returned.

        Returns:
            str: A readback or setpoint pv.
        """
        if handle == pytac.RB and self.rb_pv:
            return self.rb_pv
        elif handle == pytac.SP and self.sp_pv:
            return self.sp_pv

        raise PvException("""This device {0} has no {1} pv."""
                          .format(self.name, handle))

    def get_cs(self):
        return self._cs


class PvEnabler(object):
    def __init__(self, pv, enabled_value, cs):
        """A PvEnabler class to check whether a device is enabled.

        The class will behave like True if the pv value equals enabled_value,
        and False otherwise.

        Args:
            pv (str): pv name
            enabled_value (str): value for pv for which the device should
                be considered enabled
            cs: Control system object
        """
        self._pv = pv
        self._enabled_value = str(int(float(enabled_value)))
        self._cs = cs

    def __nonzero__(self):
        """Used to override the 'if object' clause.

        Support for Python 2.7.

        Returns:
            bool: True if the device should be considered enabled
        """
        pv_value = self._cs.get(self._pv)
        return self._enabled_value == str(int(float(pv_value)))

    def __bool__(self):
        """Used to override the 'if object' clause.

        Support for Python 3.x.

        Returns:
            bool: True if the device should be considered enabled
        """
        return self.__nonzero__()
