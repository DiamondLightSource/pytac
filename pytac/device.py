"""The device class used to represent a particular function of an accelerator
element.

A physical element in an accelerator may have multiple devices: an example at
DLS is a sextupole magnet that contains also horizontal and vertical corrector
magnets and a skew quadrupole.
"""


class Device(object):
    """A representation of a property of an element associated with a field.

    Typically a control system will be used to set and get values on a
    device.
    """
    def is_enabled(self):
        """Whether the device is enabled.

        Returns:
            bool: whether the device is enabled.
        """
        raise NotImplementedError()

    def set_value(self, value):
        """Set the value on the device.

        Args:
            value (float): the value to set.
        """
        raise NotImplementedError()

    def get_value(self):
        """Read the value from the device.

        Returns:
            float: the value of the PV.
        """
        raise NotImplementedError()


class BasicDevice(Device):
    """A basic implementation of the device class. This device does not have a
        pv associated with it, nor does it interact with a simulator. In short
        this device acts as simple storage for data that rarely changes, as it is
        not affected by changes to other aspects of the accelerator.
    """
    def __init__(self, value, enabled=True):
        """Args:
            value (?): can be a number or a list of numbers.
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

    def set_value(self, value):
        """Set the value on the device.

        Args:
            value (?): the value to set.
        """
        self.value = value

    def get_value(self, handle=None):
        """Read the value from the device.

        Returns:
            ?: the value of the PV.
        """
        return self.value
