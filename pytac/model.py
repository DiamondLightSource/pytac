"""Module containing pytac model classes."""
import pytac


class Model(object):
    """Abstract base classes for element models.

    Typically an instance would represent hardware via a control system,
    or a simulation.

    **Attributes:**

    Attributes:
        units (str): pytac.PHYS or pytac.ENG.

    **Methods:**
    """
    def get_fields(self):
        """Get all the fields represented by this model.

        Returns:
            iterable: all fields.
        """
        raise NotImplementedError()

    def get_value(self, field, handle):
        """Get a value for a field.

        Args:
            field (str): field of the requested value.
            handle (str): pytac.RB or pytac.SP

        Returns:
            float: value for specified field and handle.
        """
        raise NotImplementedError()

    def set_value(self, field, value):
        """Set a value for a field.

        This is always set to pytac.SP, never pytac.RB.

        Args:
            field (str): field to set.
            value (str): value to set.
        """
        raise NotImplementedError()


class DeviceModel(object):
    """Model containing control system devices.

    **Attributes:**

    Attributes:
        units (str): pytac.ENG or pytac.PHYS, pytac.ENG by default.

    .. Private Attributes:
           _devices (dict): A dictionary of the devices for each key(field).
    """
    def __init__(self):
        """.. The constructor method for the class, called whenever a
               'DeviceModel' object is constructed.

        **Methods:**
        """
        self._devices = {}
        self.units = pytac.ENG

    def add_device(self, field, device):
        """Add device to this model.

        Args:
            field (str): field this device represents.
            device (Device): device object.
        """
        self._devices[field] = device

    def get_device(self, field):
        """Get device from the model.

        Args:
            field (str): field of the requested device.
        Returns:
            Device: The device of the specified field.
        """
        return self._devices[field]

    def get_fields(self):
        """Get all the fields from the model.

        Returns:
            list: list of strings of all the fields of the model.
        """
        return self._devices.keys()

    def get_pv_name(self, field, handle):
        """Get pv name for a field and handle.

        Args:
            field (str): field of the requested pv.
            handle (str): pytac.RB or pytac.SP.

        Returns:
            str: pv name for specified field and handle.
        """
        return self._devices[field].get_pv_name(handle)

    def get_value(self, field, handle):
        """Get the value of a readback or setpoint pv for a field from the
        model.

        Args:
            field (str): field of the requested value.
            handle (str): pytac.RB or pytac.SP.

        Returns:
            float: The value of the pv.
        """
        return self._devices[field].get_value(handle)

    def set_value(self, field, value):
        """Set the value of a readback or setpoint pv for a field from the
        model.

        Args:
            field (str): field for the requested value.
            value (float): The value to set on the pv.
        """
        self._devices[field].set_value(value)
