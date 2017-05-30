from pytac.exceptions import PvException
import pytac


class Device(object):
    def __init__(self, cs, enabled=True, rb_pv=None, sp_pv=None):
        """A device attached on an element.

        Contains a control system, readback and setpoint pvs. A readback
        or setpoint pv is required when creating a device otherwise a
        PvException is raised. The device is enabled by default.

        Args:
            cs (ControlSystem): Control system object used to get and set
                the value of a pv.
            enabled (bool-like): Whether the device is enabled.  May be
                a PvEnabler object.
            rb_pv (string): A readback pv. This value cannot be changed.
            sp_pv (string): A setpoint pv. This value can be read and also
                changed.
        """
        self.rb_pv = rb_pv
        self.sp_pv = sp_pv
        self._cs = cs
        self._enabled = enabled
        if rb_pv is not None:
            self.name = rb_pv.split(':')[0]
        elif sp_pv is not None:
            self.name = sp_pv.split(':')[0]
        else:
            raise PvException("Readback or setpoint pvs need to be given")

    def is_enabled(self):
        """Check whether an device is enabled or disabled.

        Returns:
            boolean: Represents whether an device is enabled or disabled.
        """
        return self._enabled

    def put_value(self, value):
        """Set the value of a pv.

        If not setpoint pv exists a PvException is raised.

        Args:
            value(Number): The value to set on the pv.

        Raises:
            PvException: An exception occured when no setpoint pv exists.
        """
        # Not sure if this method will need a handle flag to set
        # an initial value for readback pvs. Suppose not:
        if self.sp_pv is not None:
            self._cs.put(self.sp_pv, value)
        else:
            raise PvException("""This device {0} has no setpoint pv."""
                              .format(self.name))

    def get_value(self, handle):
        """Read the value of a readback or setpoint pv.

        If neither readback or setpoint pvs exist then a PvException is raised.

        Args:
            handle(string): Handle used to get the value off a readback or setpoint
                pv.

        Returns:
            Number: The value off the pv.

        Raises:
            PvException: In case the requested pv doesn't exist.
        """
        if handle == pytac.RB and self.rb_pv:
            return self._cs.get(self.rb_pv)
        elif handle == pytac.SP and self.sp_pv:
            return self._cs.get(self.sp_pv)

        raise PvException("""This device {0} has no {1} pv."""
                          .format(self.name, handle))

    def get_pv_name(self, handle='*'):
        """Get a pv name on a specified handle.

        If no handle is specified, then both pvs are returned.

        Args:
            handle(string): The readback or setpoint handle to be returned.

        Returns:
            string: A readback or setpoint pv.
        """
        if handle == '*':
            return [self.rb_pv, self.sp_pv]
        elif handle == pytac.RB:
            return self.rb_pv
        elif handle == pytac.SP:
            return self.sp_pv

    def get_cs(self):
        return self._cs


class PvEnabler(object):
    def __init__(self, pv, enabled_value, cs):
        """A PvEnabler class to check whether a device is enabled.

        This object doesn't allow disabling the device.

        Args:
            pv(string): The string representation of the pv.
            enabled_value(string): A pre-defined value telling when the pv
                is enabled.
            cs: Control system object used to determine if a pv is enabled.
        """
        self._pv = pv
        self._enabled_value = str(int(float(enabled_value)))
        self._cs = cs

    def __nonzero__(self):
        """Used to override the 'if object' clause.

        Support for Python 2.7.

        Returns:
            boolean: Determining whether a device is enabled or not.
        """
        pv_value = self._cs.get(self._pv)
        return self._enabled_value == str(int(float(pv_value)))

    def __bool__(self):
        """Used to override the 'if object' clause.

        Support for Python 3.x.

        Returns:
            boolean: Determining whether a device is enabled or not.
        """
        return self.__nonzero__()
