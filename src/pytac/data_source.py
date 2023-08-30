"""Module containing pytac data source classes."""
from typing import Dict, Iterable, Optional

from _collections_abc import KeysView

import pytac
from pytac.cs import AugmentedType
from pytac.device import Device
from pytac.exceptions import DataSourceException, FieldException
from pytac.units import UnitConv


class DataSource(object):
    """Abstract base class for element or lattice data sources.

    Typically an instance would represent hardware via a control system,
    or a simulation.
    """

    units: str
    """Units of DataSource in pytac.PHYS or pytac.ENG."""

    def get_fields(self) -> Iterable:
        """Get all the fields represented by this data source.

        Returns:
            All fields.
        """
        raise NotImplementedError()

    def get_value(
        self, field: str, handle: str, throw: bool
    ) -> Optional[AugmentedType]:
        """Get a value for a field.

        Args:
            field: field of the requested value.
            handle: pytac.RB or pytac.SP
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            Value for specified field and handle.
        """
        raise NotImplementedError()

    def set_value(self, field: str, value: AugmentedType, throw: bool) -> None:
        """Set a value for a field.

        This is always set to pytac.SP, never pytac.RB.

        Args:
            field: field to set.
            value: value to set.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.
        """
        raise NotImplementedError()


class DataSourceManager(object):
    """Class that manages all the data sources and UnitConv objects associated
    with a lattice or element.

    It receives requests from a lattice or element object and directs them to
    the correct data source. The unit conversion objects for all fields are
    also held here.
    """

    default_units: str
    """Holds the current default unit type, pytac.PHYS or pytac.ENG, for an element or
        lattice."""
    default_data_source: str
    """Holds the current default data source, pytac.LIVE or pytac.SIM, for an element
        or lattice."""

    _data_sources: Dict[str, "DeviceDataSource"]
    """A dictionary of the data sources held."""
    _uc: Dict[str, UnitConv]
    """A dictionary of the unit conversion objects for each key(field)."""

    def __init__(self) -> None:
        self.default_units = pytac.ENG
        self.default_data_source = pytac.LIVE
        self._data_sources = {}
        self._uc = {}

    def set_data_source(
        self, data_source: "DeviceDataSource", data_source_type: str
    ) -> None:
        """Add a data source to the manager.

        Args:
            data_source: the data source to be set.
            data_source_type: the type of the data source being set
                pytac.LIVE or pytac.SIM.
        """
        self._data_sources[data_source_type] = data_source

    def get_data_source(self, data_source_type: str) -> "DeviceDataSource":
        """Get a data source.

        Args:
            data_source_type: the type of the data source being set
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

    def get_fields(self) -> Dict[str, Iterable]:
        """Get all the fields defined on the manager.

        Includes all fields defined by all data sources.

        Returns:
            A dictionary of all the fields defined on the manager, separated by
                data source(key).
        """
        fields: Dict[str, Iterable] = {}
        for data_source in self._data_sources:
            fields[data_source] = self._data_sources[data_source].get_fields()
        return fields

    def add_device(self, field: str, device: Device, uc: UnitConv) -> None:
        """Add device and unit conversion objects to a given field.

        A DeviceDataSource must be set before calling this method, this
        defaults to pytac.LIVE as that is the only data source that currently
        uses devices.

        Args:
            field: The key to store the unit conversion and device objects.
            device: The device object used for this field.
            uc: The unit conversion object used for this field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        self.get_data_source(pytac.LIVE).add_device(field, device)
        self.set_unitconv(field, uc)

    def get_device(self, field: str) -> Device:
        """Get the device for the given field.

        A DeviceDataSource must be set before calling this method, this
        defaults to pytac.LIVE as that is the only data source that currently
        uses devices.

        Args:
            field: The lookup key to find the device on the manager.

        Returns:
            The device on the given field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        return self.get_data_source(pytac.LIVE).get_device(field)

    def get_unitconv(self, field: str) -> UnitConv:
        """Get the unit conversion option for the specified field.

        Args:
            field: The field associated with this conversion.

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

    def set_unitconv(self, field: str, uc: UnitConv) -> None:
        """set the unit conversion option for the specified field.

        Args:
            field: The field associated with this conversion.
            uc: The unit conversion object to be set.
        """
        self._uc[field] = uc

    def get_value(
        self,
        field: str,
        handle: str = pytac.RB,
        units: str = pytac.DEFAULT,
        data_source_type: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> Optional[AugmentedType]:
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
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

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
        value: AugmentedType,
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
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

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
    """Data source containing control system devices."""

    units: str
    """pytac.ENG or pytac.PHYS, pytac.ENG by default."""

    _devices: Dict[str, Device]
    """A dictionary of the devices for each key(field)."""

    def __init__(self):
        self._devices = {}
        self.units = pytac.ENG

    def add_device(self, field: str, device: Device) -> None:
        """Add device to this data_source.

        Args:
            field: field this device represents.
            device: device object.
        """
        self._devices[field] = device

    def get_device(self, field: str) -> Device:
        """Get device from the data_source.

        Args:
            field: field of the requested device.
        Returns:
            The device of the specified field.

        Raises:
            FieldException: if the specified field doesn't exist on this data source.
        """
        try:
            return self._devices[field]
        except KeyError:
            raise FieldException(f"No field {field} on data source {self}.")

    def get_fields(self) -> KeysView:
        """Get all the fields from the data_source.

        Returns:
            List of strings of all the fields of the data_source.
        """
        return self._devices.keys()

    def get_value(
        self, field: str, handle: str, throw: bool = True
    ) -> Optional[AugmentedType]:
        """Get the value of a readback or setpoint PV for a field from the
        data_source.

        Args:
            field: field of the requested value.
            handle: pytac.RB or pytac.SP.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Returns:
            The value of the PV.

        Raises:
            FieldException: if the device does not have the specified field.
        """
        return self.get_device(field).get_value(handle, throw)

    def set_value(
        self,
        field: str,
        value: AugmentedType,
        throw: bool = True,
    ) -> None:
        """Set the value of a readback or setpoint PV for a field from the
        data_source.

        Args:
            field: field for the requested value.
            value: The value to set on the PV.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Raises:
            FieldException: if the device does not have the specified field.
        """
        self.get_device(field).set_value(value, throw)
