"""Module containing pytac data source classes."""
import pytac
from pytac.exceptions import FieldException, DeviceException, HandleException


class DataSource(object):
    """Abstract base class for element or lattice data sources.

    Typically an instance would represent hardware via a control system,
    or a simulation.

    **Attributes:**

    Attributes:
        units (str): pytac.PHYS or pytac.ENG.
        default_handle (str): pytac.RB or pytac.SP.
        default_units (str): pytac.PHYS or pytac.ENG.
        default_data_source (str): pytac.LIVE or pytac.SIM.

    **Methods:**
    """
    def get_fields(self):
        """Get all the fields represented by this data source.

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
            value (float): value to set.
        """
        raise NotImplementedError()


class DataSourceManager(object):
    """Class that manages the data sources associated with a lattice or element.

    It recieves requests from a lattice or element object and directs them to
    the correct data source. The unit conversion objects for all fields are also
    held here.

    .. Private Attributes:
           _data_sources (dict): A dictionary of the data sources held.
           _uc (dict): A dictionary of the unit conversion objects for each
                        key(field).

    **Methods:**
    """
    def __init__(self):
        self._data_sources = {}
        self._uc = {}
        self.default_handle = pytac.RB
        self.default_units = pytac.ENG
        self.default_data_source = pytac.LIVE

    def set_data_source(self, data_source, data_source_type):
        """Add a data source to the manager.

        Args:
            data_source (DataSource): the data source to be set.
            data_source_type (str): the type of the data source being set
                                     pytac.LIVE or pytac.SIM.
        """
        self._data_sources[data_source_type] = data_source

    def get_fields(self):
        """Get the all fields defined on the manager.

        Includes all fields defined by all data sources.

        Returns:
            dict: A dictionary of all the fields defined on the manager,
                   separated by data source(key).
        """
        fields = {}
        for data_source in self._data_sources:
            fields[data_source] = self._data_sources[data_source].get_fields()
        return fields

    def add_device(self, field, device, uc):
        """Add device and unit conversion objects to a given field.

        A DeviceDataSource must be set before calling this method, this defaults
        to pytac.LIVE as that is the only DeviceDataSource currently.

        Args:
            field (str): The key to store the unit conversion and device
                          objects.
            device (Device): The device object used for this field.
            uc (UnitConv): The unit conversion object used for this field.

        Raises:
            KeyError: if no DeviceDataSource is set.
        """
        self._data_sources[pytac.LIVE].add_device(field, device)
        self._uc[field] = uc

    def get_device(self, field):
        """Get the device for the given field.

        A DeviceDataSource must be set before calling this method, this defaults
        to pytac.LIVE as that is the only DeviceDataSource currently.

        Args:
            field (str): The lookup key to find the device on the manager.

        Returns:
            Device: The device on the given field.

        Raises:
            KeyError: if no DeviceDataSource is set.
        """
        return self._data_sources[pytac.LIVE].get_device(field)

    def get_unitconv(self, field):
        """Get the unit conversion option for the specified field.

        Args:
            field (str): The field associated with this conversion.

        Returns:
            UnitConv: The object associated with the specified field.

        Raises:
            KeyError: if no unit conversion object is present.
        """
        return self._uc[field]

    def get_value(self, field, handle=pytac.default, units=pytac.default,
                  data_source=pytac.default):
        """Get the value for a field.

        Returns the value of a field on the manager. This value is uniquely
        identified by a field and a handle. The returned value is either
        in engineering or physics units. The data_source flag returns either
        real or simulated values.

        Args:
            field (str): The requested field.
            handle (str): pytac.SP or pytac.RB.
            units (str): pytac.ENG or pytac.PHYS returned.
            data_source (str): pytac.LIVE or pytac.SIM.

        Returns:
            float: The value of the requested field

        Raises:
            DeviceException: if there is no device on the given field.
            FieldException: if the manager does not have the specified field.
        """
        if handle is pytac.default:
            handle = self.default_handle
        if units is pytac.default:
            units = self.default_units
        if data_source is pytac.default:
            data_source = self.default_data_source
        try:
            data_source = self._data_sources[data_source]
            value = data_source.get_value(field, handle)
            return self._uc[field].convert(value, origin=data_source.units,
                                           target=units)
        except KeyError:
            raise DeviceException('No data source type {} on manager {}'
                                  .format(data_source, self))
        except FieldException:
            raise FieldException('No field {} on manager {}'.format(field,
                                                                    self))

    def set_value(self, field, value, handle=pytac.default, units=pytac.default,
                  data_source=pytac.default):
        """Set the value for a field.

        This value can be set on the machine or the simulation.

        Args:
            field (str): The requested field.
            value (float): The value to set.
            handle (str): pytac.SP or pytac.RB.
            units (str): pytac.ENG or pytac.PHYS.
            data_source (str): pytac.LIVE or pytac.SIM.

        Raises:
            DeviceException: if arguments are incorrect.
            FieldException: if the manager does not have the specified field.
        """
        if handle is pytac.default:
            handle = self.default_handle
        if units is pytac.default:
            units = self.default_units
        if data_source is pytac.default:
            data_source = self.default_data_source
        if handle != pytac.SP:
            raise HandleException('Must write using {}'.format(pytac.SP))
        try:
            data_source = self._data_sources[data_source]
        except KeyError:
            raise DeviceException('No data source type {} on manager {}'
                                  .format(data_source, self))
        try:
            value = self._uc[field].convert(value, origin=units,
                                            target=data_source.units)
            data_source.set_value(field, value)
        except KeyError:
            raise FieldException('No field {} on manager {}'.format(data_source,
                                                                    self))
        except FieldException:
            raise FieldException('No field {} on manager {}'.format(field,
                                                                    self))


class DeviceDataSource(object):
    """Data source containing control system devices.

    **Attributes:**

    Attributes:
        units (str): pytac.ENG or pytac.PHYS, pytac.ENG by default.

    .. Private Attributes:
           _devices (dict): A dictionary of the devices for each key(field).

    **Methods:**
    """
    def __init__(self):
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
