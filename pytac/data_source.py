"""Module containing pytac model classes."""
import pytac
from pytac.exceptions import FieldException, DeviceException, HandleException


class DataSource(object):
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


class DataSourceManager(object):
    def __init__(self):
        self._models = {}
        self._uc = {}

    def set_model(self, model, model_type):
        self._models[model_type] = model

    def get_fields(self):
        fields = {}
        for model in self._models:
            fields[model] = self._models[model].get_fields()
        return fields

    def add_device(self, field, device, uc):
        self._models[pytac.LIVE].add_device(field, device)
        self._uc[field] = uc

    def get_device(self, field):
        return self._models[pytac.LIVE].get_device(field)

    def get_unitconv(self, field):
        return self._uc[field]

    def get_value(self, field, handle, units, model):
        try:
            model = self._models[model]
            value = model.get_value(field, handle)
            return self._uc[field].convert(value, origin=model.units,
                                           target=units)
        except KeyError:
            raise DeviceException('No model type {} on element {}'.format(model,
                                                                          self))
        except FieldException:
            raise FieldException('No field {} on element {}'.format(field, self))

    def set_value(self, field, value, handle, units, model):
        if handle != pytac.SP:
            raise HandleException('Must write using {}'.format(pytac.SP))
        try:
            model = self._models[model]
        except KeyError:
            raise DeviceException('No model type {} on element {}'.format(model,
                                                                          self))
        try:
            value = self._uc[field].convert(value, origin=units, target=model.units)
            model.set_value(field, value)
        except KeyError:
            raise FieldException('No field {} on element {}'.format(model, self))
        except FieldException:
            raise FieldException('No field {} on element {}'.format(field, self))


class DeviceDataSource(object):
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

    def get_value(self, field, handle):
        """Get the value of a readback or setpoint PV for a field from the
        model.

        Args:
            field (str): field of the requested value.
            handle (str): pytac.RB or pytac.SP.

        Returns:
            float: The value of the PV.

        Raises:
            FieldException: if the device does not have the specified field.
        """
        try:
            return self._devices[field].get_value(handle)
        except KeyError:
            raise FieldException('No field {} on device {}'.format(field, self))

    def set_value(self, field, value):
        """Set the value of a readback or setpoint PV for a field from the
        model.

        Args:
            field (str): field for the requested value.
            value (float): The value to set on the PV.

        Raises:
            FieldException: if the device does not have the specified field.
        """
        try:
            self._devices[field].set_value(value)
        except KeyError:
            raise FieldException('No field {} on device {}'.format(field, self))
