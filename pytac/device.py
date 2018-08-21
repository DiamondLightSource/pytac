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

    def is_enabled(self):
        return True

    def set_value(self, value):
        raise NotImplementedError()

    def get_value(self):
        raise NotImplementedError()
