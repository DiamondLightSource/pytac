"""Representation of a lattice object which contains all the elements of the
    machine.
"""
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Union, cast

import numpy
from numpy.typing import DTypeLike, NDArray

import pytac
from pytac.cs import AugmentedType, ControlSystem
from pytac.data_source import DataSourceManager, DeviceDataSource
from pytac.device import Device
from pytac.element import Element
from pytac.exceptions import DataSourceException, UnitsException
from pytac.units import UnitConv


class Lattice:
    """Representation of a lattice.

    Represents a lattice object that contains all elements of the ring. It has
    a name and a control system to be used for unit conversion.
    """

    name: str
    """The name of the lattice."""
    symmetry: Optional[int]
    """The symmetry of the lattice (the number of cells)."""

    _elements: List[Element]
    """The list of all the element objects in the lattice"""
    _data_source_manager: DataSourceManager
    """A class that manages the data sources associated with this lattice."""

    def __init__(self, name: str, symmetry: Optional[int] = None) -> None:
        """Initialise the Lattice object.

        Args:
            name: The name of the lattice.
            symmetry: The symmetry of the lattice (the number of cells).
        """
        self.name = name
        self.symmetry = symmetry
        self._elements = []
        self._data_source_manager = DataSourceManager()

    def __str__(self) -> str:
        return f"Lattice {self.name}"

    @property
    def cell_length(self) -> Optional[float]:
        """The average length of a cell in the lattice."""
        if (self.symmetry is None) or (self.get_length() == 0):
            return None
        else:
            return self.get_length() / self.symmetry

    @property
    def cell_bounds(self) -> Optional[List[int]]:
        """The indexes of elements in which a cell boundary occurs.

        Examples:
            A lattice of 5 equal length elements with 2 fold symmetry would
            return [1, 4, 5]
            1 - because it is the start of the first cell.
            4 - because it is the first element in the second cell as the
            boundary between the first and second cells occurs halfway into
            the length of element 3.
            5 - (len(lattice)) because it is the end of the second (last) cell.
        """
        if (self.symmetry is None) or (len(self._elements) == 0):
            return None
        else:
            bounds = [1]
            for cell in range(2, self.symmetry + 1, 1):
                for elem in self._elements[bounds[-1] :]:
                    if elem.cell == cell:
                        # index is not None when cell attribute is not None.
                        index = cast(int, elem.index)
                        bounds.append(index)
                        break
            bounds.append(len(self._elements))
            return bounds

    def __getitem__(self, n: int) -> Element:
        """Get the (n + 1)th element of the lattice.

        i.e. index 0 represents the first element in the lattice.

        Args:
            n: Index.

        Returns:
            Indexed element.
        """
        return self._elements[n]

    def __len__(self) -> int:
        """The number of elements in the lattice.

        Returns:
            The number of elements in the lattice.
        """
        return len(self._elements)

    def set_data_source(
        self, data_source: DeviceDataSource, data_source_type: str
    ) -> None:
        """Add a data source to the lattice.

        Args:
            data_source: the data source to be set.
            data_source_type: the type of the data source being set;
                pytac.LIVE or pytac.SIM.
        """
        self._data_source_manager.set_data_source(data_source, data_source_type)

    def get_fields(self) -> Dict[str, Iterable]:
        """Get the fields defined on the lattice.

        Includes all fields defined by all data sources.

        Returns:
            A dictionary of all the fields defined on the lattice, separated by
                data source(key).
        """
        return self._data_source_manager.get_fields()

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
        self._data_source_manager.add_device(field, device, uc)

    def get_device(self, field: str) -> Device:
        """Get the device for the given field.

        A DeviceDataSource must be set before calling this method, this
        defaults to pytac.LIVE as that is the only data source that currently
        uses devices.

        Args:
            field: The lookup key to find the device on the lattice.

        Returns:
            The device on the given field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        return self._data_source_manager.get_device(field)

    def get_unitconv(self, field: str) -> UnitConv:
        """Get the unit conversion option for the specified field.

        Args:
            field: The field associated with this conversion.

        Returns:
            The object associated with the specified field.

        Raises:
            FieldException: if no unit conversion object is present.
        """
        return self._data_source_manager.get_unitconv(field)

    def set_unitconv(self, field: str, uc: UnitConv) -> None:
        """Set the unit conversion option for the specified field.

        Args:
            field: The field associated with this conversion.
            uc: The unit conversion object to be set.
        """
        self._data_source_manager.set_unitconv(field, uc)

    def get_value(
        self,
        field: str,
        handle: str = pytac.RB,
        units: str = pytac.DEFAULT,
        data_source: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> Optional[AugmentedType]:
        """Get the value for a field on the lattice.

        Returns the value of a field on the lattice. This value is uniquely
        identified by a field and a handle. The returned value is either
        in engineering or physics units. The data_source flag returns either
        real or simulated values.

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
            FieldException: if the lattice does not have the specified field.
        """
        return self._data_source_manager.get_value(
            field, handle, units, data_source, throw
        )

    def set_value(
        self,
        field: str,
        value: AugmentedType,
        units: str = pytac.DEFAULT,
        data_source: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> None:
        """Set the value for a field.

        This value can be set on the machine or the simulation.

        Args:
            field: The requested field.
            value: The value to set.
            units: pytac.ENG or pytac.PHYS.
            data_source: pytac.LIVE or pytac.SIM.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Raises:
            DataSourceException: if arguments are incorrect.
            FieldException: if the lattice does not have the specified field.
        """
        self._data_source_manager.set_value(field, value, units, data_source, throw)

    def get_length(self) -> float:
        """Returns the length of the lattice, in meters.

        Returns:
            The length of the lattice (m).
        """
        total_length = 0.0
        for e in self._elements:
            total_length += e.length
        return total_length

    def add_element(self, element: Element) -> None:
        """Append an element to the lattice and update its lattice reference.

        Args:
            element: element to append.
        """
        element.set_lattice(self)
        self._elements.append(element)

    def get_elements(
        self, family: Optional[str] = None, cell: Optional[int] = None
    ) -> List[Element]:
        """Get the elements of a family from the lattice.

        If no family is specified it returns all elements. Elements are
        returned in the order they exist in the ring.

        Args:
            family: requested family.
            cell: restrict elements to those in the specified cell.

        Returns:
            List containing all elements of the specified family.

        Raises:
            ValueError: if there are no elements in the specified cell or family.
        """
        if family is None:
            elements = self._elements[:]
            if len(elements) == 0:
                raise ValueError(f"No elements in lattice {self}.")
        else:
            elements = [e for e in self._elements if e.is_in_family(family)]
            if len(elements) == 0:
                raise ValueError(f"{self}: no elements in family {family}.")
        if cell is not None:
            elements = [e for e in elements if e.cell == cell]
            if len(elements) == 0:
                raise ValueError(f"{self}: no elements in cell {cell}.")
        return elements

    def get_all_families(self) -> Set[Any]:
        """Get all families of elements in the lattice.

        Returns:
            set: all defined families.
        """
        families = set()
        for element in self._elements:
            families.update(element.families)
        return families

    def get_family_s(self, family: str) -> List[float]:
        """Get s positions for all elements from the same family.

        Args:
            family: requested family.

        Returns:
            List of s positions for each element.
        """
        elements = self.get_elements(family)
        s_positions = []
        for element in elements:
            assert element.s is not None
            s_positions.append(element.s)
        return s_positions

    def get_element_devices(self, family: str, field: str) -> List[Device]:
        """Get devices for a specific field for elements in the specfied
        family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have a device for fields 'x'
        and 'y'.

        Args:
            family: family of elements.
            field: field specifying the devices.

        Returns:
            Devices for specified family and field.
        """
        elements = self.get_elements(family)
        devices: List[Device] = []
        for element in elements:
            try:
                devices.append(element.get_device(field))
            except DataSourceException:
                logging.warning(f"No device for field {field} on element {element}.")
        return devices

    def get_element_device_names(self, family: str, field: str) -> List[str]:
        """Get the names for devices attached to a specific field for elements
        in the specfied family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have a device for fields 'x'
        and 'y'.

        Args:
            family: family of elements.
            field: field specifying the devices.

        Returns:
            list: device names for specified family and field.
        """
        devices = self.get_element_devices(family, field)
        return [device.name for device in devices]

    def get_element_values(
        self,
        family: str,
        field: str,
        handle: str = pytac.RB,
        units: str = pytac.DEFAULT,
        data_source: str = pytac.DEFAULT,
        throw: bool = True,
        dtype: Optional[DTypeLike] = None,
    ) -> Union[List[Optional[AugmentedType]], NDArray]:
        """Get the value of the given field for all elements in the given
        family in the lattice.

        Args:
            family: family of elements to request the values of.
            field: field to request values for.
            handle: pytac.RB or pytac.SP.
            units: pytac.ENG or pytac.PHYS.
            data_source: pytac.LIVE or pytac.SIM.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.
            dtype: if None, return a list. If not None, return a numpy array of the
                specified type.

        Returns:
            The requested values.
        """
        elements = self.get_elements(family)
        values: List[Optional[AugmentedType]] = [
            element.get_value(field, handle, units, data_source, throw)
            for element in elements
        ]
        if dtype is not None:
            array_values: NDArray = numpy.array(values, dtype=dtype)
            return array_values
        return values

    def set_element_values(
        self,
        family: str,
        field: str,
        values: Sequence[AugmentedType],
        units: str = pytac.DEFAULT,
        data_source: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> None:
        """Set the value of the given field for all elements in the given
        family in the lattice to the given values.

        Args:
            family: family of elements on which to set values.
            field:  field to set values for.
            values: A list of values to assign.
            units: pytac.ENG or pytac.PHYS.
            data_source: pytac.LIVE or pytac.SIM.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Raises:
            IndexError: if the given list of values doesn't match the number of
                elements in the family.
        """
        elements = self.get_elements(family)
        if len(elements) != len(values):
            raise IndexError(
                f"Number of elements in given array({len(values)}) must be "
                f"equal to the number of elements in the family({len(elements)})."
            )
        for element, value in zip(elements, values):
            status = element.set_value(
                field,
                value,
                units=units,
                data_source=data_source,
                throw=throw,
            )
            if status is not None:
                return status

    def set_default_units(self, units: str) -> None:
        """Sets the default unit type for the lattice and all its elements.

        Args:
            default_units: The default unit type to be set across the entire lattice,
                pytac.ENG or pytac.PHYS.

        Raises:
            UnitsException: if specified default unit type is not a valid unit type.
        """
        if units == pytac.ENG or units == pytac.PHYS:
            self._data_source_manager.default_units = units
            elems = self.get_elements()
            for elem in elems:
                elem.set_default_units(units)
        else:
            raise UnitsException(
                f"{units} is not a unit type. Please enter {pytac.ENG} or {pytac.PHYS}."
            )

    def set_default_data_source(self, data_source_type: str) -> None:
        """Sets the default data source for the lattice and all its elements.

        Args:
            data_source_type: The default data source to be set across the entire
                lattice, pytac.LIVE or pytac.SIM.

        Raises:
            DataSourceException: if specified default data source is not a valid
                data source.
        """
        if (data_source_type == pytac.LIVE) or (data_source_type == pytac.SIM):
            self._data_source_manager.default_data_source = data_source_type
            elems = self.get_elements()
            for elem in elems:
                elem._data_source_manager.default_data_source = data_source_type
        else:
            raise DataSourceException(
                f"{data_source_type} is not a data source. "
                f"Please enter {pytac.LIVE} or {pytac.SIM}."
            )

    def get_default_units(self) -> str:
        """Get the default unit type, pytac.ENG or pytac.PHYS.

        Returns:
            The default unit type for the entire lattice.
        """
        return self._data_source_manager.default_units

    def get_default_data_source(self) -> str:
        """Get the default data source, pytac.LIVE or pytac.SIM.

        Returns:
            The default data source for the entire lattice.
        """
        return self._data_source_manager.default_data_source

    def convert_family_values(
        self,
        family: str,
        field: str,
        values: Sequence[Optional[AugmentedType]],
        origin: str,
        target: str,
    ) -> List[Optional[AugmentedType]]:
        """Convert the given values according to the given origin and target
        units, using the unit conversion objects for the given field on the
        elements in the given family.

        Args:
            family: the family of elements which the values belong to.
            field: the field on the elements which the values are from.
            values: values to be converted.
            origin: pytac.ENG or pytac.PHYS.
            target: pytac.ENG or pytac.PHYS.
        """
        elements = self.get_elements(family)
        if len(elements) != len(values):
            raise IndexError(
                f"Number of elements in given sequence({len(values)}) must "
                f"be equal to the number of elements in the family({len(elements)})."
            )
        converted_values = []
        for elem, value in zip(elements, values):
            uc = elem.get_unitconv(field)
            converted_values.append(uc.convert(value, origin, target))
        return converted_values


class EpicsLattice(Lattice):
    """EPICS-aware lattice class.

    Allows efficient get_element_values() and set_element_values() methods,
    and adds get_pv_names() method.

    Attributes:
        name: The name of the lattice.
        symmetry: The symmetry of the lattice (the number of cells).

    .. Private Attributes:
            _elements: The list of all the element objects in the lattice
            _cs: The control system to use for the more efficient batch getting and
                setting of PVs.
            _data_source_manager: A class that manages the data sources associated
                with this lattice.
    """

    _cs: ControlSystem

    def __init__(
        self, name: str, epics_cs: ControlSystem, symmetry: Optional[int] = None
    ) -> None:
        """
        Args:
            name: The name of the epics lattice.
            epics_cs: The control system used to store the values on a PV.
            symmetry: The symmetry of the lattice (the number of cells).
        """
        super(EpicsLattice, self).__init__(name, symmetry)
        self._cs = epics_cs

    def get_pv_name(self, field: str, handle: str) -> str:
        """Get the PV name for a specific field, and handle on this lattice.

        Args:
            field: The requested field.
            handle: pytac.RB or pytac.SP.

        Returns:
            The readback or setpoint PV for the specified field.
        """
        try:
            return (
                self._data_source_manager.get_data_source(pytac.LIVE)
                .get_device(field)
                .get_pv_name(handle)
            )
        except AttributeError:
            raise DataSourceException(
                f"Cannot get PV for field {field} on lattice "
                f"{self}, as the device does not have associated PVs."
            )

    def get_element_pv_names(self, family: str, field: str, handle: str) -> List[str]:
        """Get the PV names for the given field, and handle, on all elements
        in the given family in the lattice.

        Assume that the elements are EpicsElements that have the get_pv_name() method.

        Args:
            family: The requested family.
            field: The requested field.
            handle: pytac.RB or pytac.SP.

        Returns:
            A list of PV names, strings.
        """
        elements = self.get_elements(family)
        pv_names = []
        for element in elements:
            pv_names.append(element.get_pv_name(field, handle))
        return pv_names

    def get_element_values(
        self,
        family: str,
        field: str,
        handle: str = pytac.RB,
        units: str = pytac.DEFAULT,
        data_source: str = pytac.DEFAULT,
        throw: bool = True,
        dtype: Optional[DTypeLike] = None,
    ) -> Union[List[Optional[AugmentedType]], NDArray]:
        """Get the value of the given field for all elements in the given
        family in the lattice.

        Args:
            family: family of elements to request the values of.
            field: field to request values for.
            handle: pytac.RB or pytac.SP.
            units: pytac.ENG or pytac.PHYS.
            data_source: pytac.LIVE or pytac.SIM.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.
            dtype: if None, return a list. If not None, return a numpy array of the
                specified type.

        Returns:
            The requested values.
        """
        values: Union[List[Optional[AugmentedType]], NDArray] = []

        if data_source == pytac.DEFAULT:
            data_source = self.get_default_data_source()
        if units == pytac.DEFAULT:
            units = self.get_default_units()
        if data_source == pytac.LIVE:
            pv_names = self.get_element_pv_names(family, field, handle)
            values = self._cs.get_multiple(pv_names, throw)
            if units == pytac.PHYS:
                values = self.convert_family_values(
                    family, field, values, pytac.ENG, pytac.PHYS
                )
        else:
            values = super(EpicsLattice, self).get_element_values(
                family, field, handle, units, data_source, throw
            )
        if dtype is not None:
            array_values: NDArray = numpy.array(values, dtype=dtype)
            return array_values
        return values

    def set_element_values(
        self,
        family: str,
        field: str,
        values: Sequence[AugmentedType],
        units: str = pytac.DEFAULT,
        data_source: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> None:
        """Set the value of the given field for all elements in the given
        family in the lattice to the given values.

        Args:
            family: family of elements on which to set values.
            field:  field to set values for.
            values: A list of values to assign.
            units: pytac.ENG or pytac.PHYS.
            data_source: pytac.LIVE or pytac.SIM.
            throw: On failure: if True, raise ControlSystemException; if False, None
                will be returned for any PV that fails and a warning will be logged.

        Raises:
            IndexError: if the given list of values doesn't match the number of
                elements in the family.
        """
        if data_source == pytac.DEFAULT:
            data_source = self.get_default_data_source()
        if units == pytac.DEFAULT:
            units = self.get_default_units()
        if data_source == pytac.LIVE:
            if units == pytac.PHYS:
                values_result = self.convert_family_values(
                    family, field, values, pytac.PHYS, pytac.ENG
                )
            else:
                values_result = [
                    cast(Optional[AugmentedType], value) for value in values
                ]
            pv_names = self.get_element_pv_names(family, field, pytac.SP)
            if len(pv_names) != len(values_result):
                raise IndexError(
                    f"Number of elements in given sequence({len(values)}) "
                    "must be equal to the number of elements in "
                    f"the family({len(pv_names)})."
                )
            # There is no reason to ever set a PV to None.
            values_result_cast = cast(List[AugmentedType], values_result)
            self._cs.set_multiple(pv_names, values_result_cast, throw)
        else:
            super(EpicsLattice, self).set_element_values(
                family, field, values, units, data_source, throw
            )
