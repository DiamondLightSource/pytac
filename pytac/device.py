"""The device class used to represent a particular function of an accelerator
element.

A physical element in an accelerator may have multiple devices: an example at
DLS is a sextupole magnet that contains also horizontal and vertical corrector
magnets and a skew quadrupole.
"""


class DeviceException(Exception):
    """Exception associated with Device misconfiguration or invalid requests.
    """
    pass


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
