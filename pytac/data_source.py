"""Module containing pytac data source classes."""
import pytac
from pytac.exceptions import FieldException, DeviceException, HandleException


class DataSource(object):
    """Abstract base classes for element data_sources.

    Typically an instance would represent hardware via a control system,
    or a simulation.

    **Attributes:**

    Attributes:
        units (str): pytac.PHYS or pytac.ENG.

    **Methods:**
    """
    def get_fields(self):
        """Get all the fields represented by this data_source.

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
        self._data_sources = {}
        self._uc = {}

    def set_data_source(self, data_source, data_source_type):
        self._data_sources[data_source_type] = data_source

    def get_fields(self):
        fields = {}
        for data_source in self._data_sources:
            fields[data_source] = self._data_sources[data_source].get_fields()
        return fields

    def add_device(self, field, device, uc):
        self._data_sources[pytac.LIVE].add_device(field, device)
        self._uc[field] = uc

    def get_device(self, field):
        return self._data_sources[pytac.LIVE].get_device(field)

    def get_unitconv(self, field):
        return self._uc[field]

    def get_value(self, field, handle, units, data_source):
        try:
            data_source = self._data_sources[data_source]
            value = data_source.get_value(field, handle)
            return self._uc[field].convert(value, origin=data_source.units,
                                           target=units)
        except KeyError:
            raise DeviceException('No data_source type {} on element {}'.format(data_source, self))
        except FieldException:
            raise FieldException('No field {} on element {}'.format(field, self))

    def set_value(self, field, value, handle, units, data_source):
        if handle != pytac.SP:
            raise HandleException('Must write using {}'.format(pytac.SP))
        try:
            data_source = self._data_sources[data_source]
        except KeyError:
            raise DeviceException('No data_source type {} on element {}'.format(data_source, self))
        try:
            value = self._uc[field].convert(value, origin=units, target=data_source.units)
            data_source.set_value(field, value)
        except KeyError:
            raise FieldException('No field {} on element {}'.format(data_source, self))
        except FieldException:
            raise FieldException('No field {} on element {}'.format(field, self))


class DeviceDataSource(object):
    """Data source containing control system devices.

    **Attributes:**

    Attributes:
        units (str): pytac.ENG or pytac.PHYS, pytac.ENG by default.

    .. Private Attributes:
           _devices (dict): A dictionary of the devices for each key(field).
    """
    def __init__(self):
        """.. The constructor method for the class, called whenever a
               'DeviceDataSource' object is constructed.

        **Methods:**
        """
        self._devices = {}
        self.units = pytac.ENG

    def add_device(self, field, device):
        """Add device to this data_source.

        Args:
            field (str): field this device represents.
            device (Device): device object.
        """
        self._devices[field] = device

    def get_device(self, field):
        """Get device from the data_source.

        Args:
            field (str): field of the requested device.
        Returns:
            Device: The device of the specified field.
        """
        return self._devices[field]

    def get_fields(self):
        """Get all the fields from the data_source.

        Returns:
            list: list of strings of all the fields of the data_source.
        """
        return self._devices.keys()

    def get_value(self, field, handle):
        """Get the value of a readback or setpoint PV for a field from the
        data_source.

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
        data_source.

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
