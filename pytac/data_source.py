"""Module containing pytac data source classes."""
import pytac
from pytac.exceptions import DataSourceException, FieldException


class DataSource(object):
    """Abstract base class for element or lattice data sources.

    Typically an instance would represent hardware via a control system,
    or a simulation.

    **Attributes:**

    Attributes:
        units (str): pytac.PHYS or pytac.ENG.

    **Methods:**
    """

    def get_fields(self):
        """Get all the fields represented by this data source.

        Returns:
            iterable: all fields.
        """
        raise NotImplementedError()

    def get_value(self, field, handle, throw):
        """Get a value for a field.

        Args:
            field (str): field of the requested value.
            handle (str): pytac.RB or pytac.SP
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            float: value for specified field and handle.
        """
        raise NotImplementedError()

    def set_value(self, field, value, throw):
        """Set a value for a field.

        This is always set to pytac.SP, never pytac.RB.

        Args:
            field (str): field to set.
            value (float): value to set.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.
        """
        raise NotImplementedError()


class DataSourceManager(object):
    """Class that manages all the data sources and UnitConv objects associated
    with a lattice or element.

    It receives requests from a lattice or element object and directs them to
    the correct data source. The unit conversion objects for all fields are
    also held here.

    Attributes:
        default_units (str): Holds the current default unit type, pytac.PHYS or
                              pytac.ENG, for an element or lattice.
        default_data_source (str): Holds the current default data source,
                                    pytac.LIVE or pytac.SIM, for an element or
                                    lattice.

    .. Private Attributes:
           _data_sources (dict): A dictionary of the data sources held.
           _uc (dict): A dictionary of the unit conversion objects for each
                        key(field).

    **Methods:**
    """

    def __init__(self):
        self._data_sources = {}
        self._uc = {}
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

    def get_data_source(self, data_source_type):
        """Get a data source.

        Args:
            data_source_type (str): the type of the data source being set
                                     pytac.LIVE or pytac.SIM.

        Raises:
            DataSourceException: if there is no data source on the given field.
            """
        try:
            return self._data_sources[data_source_type]
        except KeyError:
            raise DataSourceException(
                f"No data source {data_source_type} on manager {self}."
            )

    def get_fields(self):
        """Get all the fields defined on the manager.

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

        A DeviceDataSource must be set before calling this method, this
        defaults to pytac.LIVE as that is the only data source that currently
        uses devices.

        Args:
            field (str): The key to store the unit conversion and device
                          objects.
            device (Device): The device object used for this field.
            uc (UnitConv): The unit conversion object used for this field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        self.get_data_source(pytac.LIVE).add_device(field, device)
        self.set_unitconv(field, uc)

    def get_device(self, field):
        """Get the device for the given field.

        A DeviceDataSource must be set before calling this method, this
        defaults to pytac.LIVE as that is the only data source that currently
        uses devices.

        Args:
            field (str): The lookup key to find the device on the manager.

        Returns:
            Device: The device on the given field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        return self.get_data_source(pytac.LIVE).get_device(field)

    def get_unitconv(self, field):
        """Get the unit conversion option for the specified field.

        Args:
            field (str): The field associated with this conversion.

        Returns:
            UnitConv: The object associated with the specified field.

        Raises:
            FieldException: if no unit conversion object is present.
        """
        try:
            return self._uc[field]
        except KeyError:
            raise FieldException(
                f"No unit conversion option for field {field} on manager {self}."
            )

    def set_unitconv(self, field, uc):
        """set the unit conversion option for the specified field.

        Args:
            field (str): The field associated with this conversion.
            uc (UnitConv): The unit conversion object to be set.
        """
        self._uc[field] = uc

    def get_value(
        self,
        field: str,
        handle: str = pytac.RB,
        units: str = pytac.DEFAULT,
        data_source_type: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> float:
        """Get the value for a field.

        Returns the value of a field on the manager. This value is uniquely
        identified by a field and a handle. The returned value is either
        in engineering or physics units. The data_source flag returns either
        real or simulated values. If handle, units or data_source are not given
        then the lattice default values are used.

        Args:
            field: The requested field.
            handle: pytac.SP or pytac.RB.
            units: pytac.ENG or pytac.PHYS returned.
            data_source: pytac.LIVE or pytac.SIM.
            throw: On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            The value of the requested field

        Raises:
            DataSourceException: if there is no data source on the given field.
            FieldException: if the manager does not have the specified field.
        """
        if units == pytac.DEFAULT:
            units = self.default_units
        if data_source_type == pytac.DEFAULT:
            data_source_type = self.default_data_source
        data_source = self.get_data_source(data_source_type)
        value = data_source.get_value(field, handle, throw)
        return self.get_unitconv(field).convert(
            value, origin=data_source.units, target=units
        )

    def set_value(
        self,
        field: str,
        value: float,
        units: str = pytac.DEFAULT,
        data_source_type: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> None:
        """Set the value for a field.

        This sets a value on the machine or the simulation. If handle,units or
        data_source are not given then the lattice default values are used.

        Args:
            field: The requested field.
            value: The value to set.
            units: pytac.ENG or pytac.PHYS.
            data_source_type: pytac.LIVE or pytac.SIM.
            throw: On failure: if True, raise ControlSystemException: if
                           False, log a warning.

        Raises:
            HandleException: if the specified handle is not pytac.SP.
            DataSourceException: if arguments are incorrect.
            FieldException: if the manager does not have the specified field.
        """
        if units == pytac.DEFAULT:
            units = self.default_units
        if data_source_type == pytac.DEFAULT:
            data_source_type = self.default_data_source
        data_source = self.get_data_source(data_source_type)
        value = self.get_unitconv(field).convert(
            value, origin=units, target=data_source.units
        )
        data_source.set_value(field, value, throw)


class DeviceDataSource(DataSource):
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

        Raises:
            FieldException: if the specified field doesn't exist on this data
                             source.
        """
        try:
            return self._devices[field]
        except KeyError:
            raise FieldException(f"No field {field} on data source {self}.")

    def get_fields(self):
        """Get all the fields from the data_source.

        Returns:
            list: list of strings of all the fields of the data_source.
        """
        return self._devices.keys()

    def get_value(self, field, handle, throw=True):
        """Get the value of a readback or setpoint PV for a field from the
        data_source.

        Args:
            field (str): field of the requested value.
            handle (str): pytac.RB or pytac.SP.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            float: The value of the PV.

        Raises:
            FieldException: if the device does not have the specified field.
        """
        return self.get_device(field).get_value(handle, throw)

    def set_value(self, field, value, throw=True):
        """Set the value of a readback or setpoint PV for a field from the
        data_source.

        Args:
            field (str): field for the requested value.
            value (float): The value to set on the PV.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.

        Raises:
            FieldException: if the device does not have the specified field.
        """
        self.get_device(field).set_value(value, throw)
