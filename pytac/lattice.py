"""Representation of a lattice object which contains all the elements of the
    machine.
"""
import logging

import numpy

import pytac
from pytac.data_source import DataSourceManager
from pytac.exceptions import (DataSourceException, FieldException,
                              UnitsException, HandleException)


class Lattice(object):
    """Representation of a lattice.

    Represents a lattice object that contains all elements of the ring. It has
    a name and a control system to be used for unit conversion.

    **Attributes:**

    Attributes:
        name (str): The name of the lattice.
        symmetry (int): The symmetry of the lattice (the number of cells).

    .. Private Attributes:
           _elements (list): The list of all the element objects in the lattice
           _data_source_manager (DataSourceManager): A class that manages the
                                                      data sources associated
                                                      with this lattice.
    """
    def __init__(self, name, symmetry=None):
        """Args:
            name (str): The name of the lattice.
            symmetry (int): The symmetry of the lattice (the number of cells).

        **Methods:**
        """
        self.name = name
        self.symmetry = symmetry
        self._elements = []
        self._data_source_manager = DataSourceManager()

    @property
    def cell_length(self):
        """float: The average length of a cell in the lattice.
        """
        if (self.symmetry is None) or (self.get_length() == 0):
            return None
        else:
            return self.get_length() / self.symmetry

    @property
    def cell_bounds(self):
        """list (str): The indexes of elements in which a cell boundary occurs.

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
                for elem in self._elements[bounds[-1]:]:
                    if elem.cell == cell:
                        bounds.append(elem.index)
                        break
            bounds.append(len(self._elements))
            return bounds

    def __getitem__(self, n):
        """Get the (n + 1)th element of the lattice.

        i.e. index 0 represents the first element in the lattice.

        Args:
            n (int): index.

        Returns:
            Element: indexed element.
        """
        return self._elements[n]

    def __len__(self):
        """The number of elements in the lattice.

        Returns:
            int: The number of elements in the lattice.
        """
        return len(self._elements)

    def set_data_source(self, data_source, data_source_type):
        """Add a data source to the lattice.

        Args:
            data_source (DataSource): the data source to be set.
            data_source_type (str): the type of the data source being set
                                     pytac.LIVE or pytac.SIM.
        """
        self._data_source_manager.set_data_source(data_source,
                                                  data_source_type)

    def get_fields(self):
        """Get the fields defined on the lattice.

        Includes all fields defined by all data sources.

        Returns:
            dict: A dictionary of all the fields defined on the lattice,
                   separated by data source(key).
        """
        return self._data_source_manager.get_fields()

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
        try:
            self._data_source_manager.add_device(field, device, uc)
        except DataSourceException:
            raise DataSourceException("No device data source on lattice {0}."
                                      .format(self))

    def get_device(self, field):
        """Get the device for the given field.

        A DeviceDataSource must be set before calling this method, this
        defaults to pytac.LIVE as that is the only data source that currently
        uses devices.

        Args:
            field (str): The lookup key to find the device on the lattice.

        Returns:
            Device: The device on the given field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        try:
            return self._data_source_manager.get_device(field)
        except DataSourceException:
            raise DataSourceException("No device data source on lattice {0}."
                                      .format(self))

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
            return self._data_source_manager.get_unitconv(field)
        except FieldException:
            raise FieldException("No unit conversion option for field {0} on "
                                 "lattice {1}.".format(field, self))

    def set_unitconv(self, field, uc):
        """Set the unit conversion option for the specified field.

        Args:
            field (str): The field associated with this conversion.
            uc (UnitConv): The unit conversion object to be set.
        """
        self._data_source_manager.set_unitconv(field, uc)

    def get_value(self, field, handle=pytac.RB, units=pytac.DEFAULT,
                  data_source=pytac.DEFAULT, throw=True):
        """Get the value for a field on the lattice.

        Returns the value of a field on the lattice. This value is uniquely
        identified by a field and a handle. The returned value is either
        in engineering or physics units. The data_source flag returns either
        real or simulated values.

        Args:
            field (str): The requested field.
            handle (str): pytac.SP or pytac.RB.
            units (str): pytac.ENG or pytac.PHYS returned.
            data_source (str): pytac.LIVE or pytac.SIM.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, return None and log a warning.

        Returns:
            float: The value of the requested field

        Raises:
            DataSourceException: if there is no data source on the given field.
            FieldException: if the lattice does not have the specified field.
        """
        try:
            return self._data_source_manager.get_value(field, handle, units,
                                                       data_source, throw)
        except DataSourceException:
            raise DataSourceException("No data source {0} on lattice {1}."
                                      .format(data_source, self))
        except FieldException:
            raise FieldException("Lattice {0} does not have field {1} on data "
                                 "source {2}".format(self, field, data_source))

    def set_value(self, field, value, handle=pytac.SP, units=pytac.DEFAULT,
                  data_source=pytac.DEFAULT, throw=True):
        """Set the value for a field.

        This value can be set on the machine or the simulation.

        Args:
            field (str): The requested field.
            value (float): The value to set.
            handle (str): pytac.SP or pytac.RB.
            units (str): pytac.ENG or pytac.PHYS.
            data_source (str): pytac.LIVE or pytac.SIM.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.

        Raises:
            DataSourceException: if arguments are incorrect.
            FieldException: if the lattice does not have the specified field.
        """
        try:
            self._data_source_manager.set_value(field, value, handle, units,
                                                data_source, throw)
        except DataSourceException:
            raise DataSourceException("No data source {0} on lattice {1}."
                                      .format(data_source, self))
        except FieldException:
            raise FieldException("Lattice {0} does not have field {1} on data "
                                 "source {2}".format(self, field, data_source))

    def get_length(self):
        """Returns the length of the lattice, in meters.

        Returns:
            float: The length of the lattice (m).
        """
        total_length = 0.0
        for e in self._elements:
            total_length += e.length
        return total_length

    def add_element(self, element):
        """Append an element to the lattice and update its lattice reference.

        Args:
            element (Element): element to append.
        """
        element.set_lattice(self)
        self._elements.append(element)

    def get_elements(self, family=None, cell=None):
        """Get the elements of a family from the lattice.

        If no family is specified it returns all elements. Elements are
        returned in the order they exist in the ring.

        Args:
            family (str): requested family.
            cell (int): restrict elements to those in the specified cell.

        Returns:
            list: list containing all elements of the specified family.

        Raises:
            ValueError: if there are no elements in the specified cell or
                         family.
        """
        if family is None:
            elements = self._elements[:]
            if len(elements) == 0:
                raise ValueError("No elements in lattice {0}.".format(self))
        else:
            elements = [e for e in self._elements if family in e.families]
            if len(elements) == 0:
                raise ValueError("No elements in family {0}.".format(family))
        if cell is not None:
            elements = [e for e in elements if e.cell == cell]
            if len(elements) == 0:
                raise ValueError("No elements in cell {0}.".format(cell))
        return elements

    def get_all_families(self):
        """Get all families of elements in the lattice.

        Returns:
            set: all defined families.
        """
        families = set()
        for element in self._elements:
            families.update(element.families)
        return families

    def get_family_s(self, family):
        """Get s positions for all elements from the same family.

        Args:
            family (str): requested family.

        Returns:
            list: list of s positions for each element.
        """
        elements = self.get_elements(family)
        s_positions = []
        for element in elements:
            s_positions.append(element.s)
        return s_positions

    def get_element_devices(self, family, field):
        """Get devices for a specific field for elements in the specfied
        family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have a device for fields 'x'
        and 'y'.

        Args:
            family (str): family of elements.
            field (str): field specifying the devices.

        Returns:
            list: devices for specified family and field.
        """
        elements = self.get_elements(family)
        devices = []
        for element in elements:
            try:
                devices.append(element.get_device(field))
            except DataSourceException:
                logging.warning("No device for field {0} on element {1}."
                                .format(field, element))
        return devices

    def get_element_device_names(self, family, field):
        """Get the names for devices attached to a specific field for elements
        in the specfied family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have a device for fields 'x'
        and 'y'.

        Args:
            family (str): family of elements.
            field (str): field specifying the devices.

        Returns:
            list: device names for specified family and field.
        """
        devices = self.get_element_devices(family, field)
        return [device.name for device in devices]

    def get_element_values(self, family, field, handle=pytac.RB,
                           units=pytac.DEFAULT, data_source=pytac.DEFAULT,
                           throw=True, dtype=None):
        """Get the value of the given field for all elements in the given
        family in the lattice.

        Args:
            family (str): family of elements to request the values of.
            field (str): field to request values for.
            handle (str): pytac.RB or pytac.SP.
            units (str): pytac.ENG or pytac.PHYS.
            data_source (str): pytac.LIVE or pytac.SIM.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, None will be returned for any PV that fails
                           and a warning will be logged.
            dtype (numpy.dtype): if None, return a list. If not None, return a
                                  numpy array of the specified type.

        Returns:
            list or numpy.array: The requested values.
        """
        elements = self.get_elements(family)
        values = [element.get_value(field, handle, units, data_source, throw)
                  for element in elements]
        if dtype is not None:
            values = numpy.array(values, dtype=dtype)
        return values

    def set_element_values(self, family, field, values, handle=pytac.SP,
                           units=pytac.DEFAULT, data_source=pytac.DEFAULT,
                           throw=True):
        """Set the value of the given field for all elements in the given
        family in the lattice to the given values.

        Args:
            family (str): family of elements on which to set values.
            field (str):  field to set values for.
            values (sequence): A list of values to assign.
            handle (str): pytac.SP or pytac.RB.
            units (str): pytac.ENG or pytac.PHYS.
            data_source (str): pytac.LIVE or pytac.SIM.
            throw (bool): On failure, if True raise ControlSystemException, if
                           False return a list of True and False values
                           corresponding to successes and failures and log a
                           warning for each PV that fails.

        Raises:
            IndexError: if the given list of values doesn't match the number of
                         elements in the family.
        """
        if handle != pytac.SP:
            raise HandleException("Must write using {0}.".format(pytac.SP))
        elements = self.get_elements(family)
        if len(elements) != len(values):
            raise IndexError("Number of elements in given array({0}) must be "
                             "equal to the number of elements in the "
                             "family({1}).".format(len(values), len(elements)))
        for element, value in zip(elements, values):
            status = element.set_value(field, value, handle=pytac.SP,
                                       units=units, data_source=data_source,
                                       throw=throw)
            if status is not None:
                return status

    def set_default_units(self, default_units):
        """Sets the default unit type for the lattice and all its elements.

        Args:
            default_units (str): The default unit type to be set across the
                                  entire lattice, pytac.ENG or pytac.PHYS.

        Raises:
            UnitsException: if specified default unit type is not a valid unit
                             type.
        """
        if default_units == pytac.ENG or default_units == pytac.PHYS:
            self._data_source_manager.default_units = default_units
            elems = self.get_elements()
            for elem in elems:
                elem._data_source_manager.default_units = default_units
        elif default_units is not None:
            raise UnitsException("{0} is not a unit type. Please enter {1} or "
                                 "{2}.".format(default_units, pytac.ENG,
                                               pytac.PHYS))

    def set_default_data_source(self, default_ds):
        """Sets the default data source for the lattice and all its elements.

        Args:
            default_ds (str): The default data source to be set across the
                               entire lattice, pytac.LIVE or pytac.SIM.

        Raises:
            DataSourceException: if specified default data source is not a
                                  valid data source.
        """
        if (default_ds == pytac.LIVE) or (default_ds == pytac.SIM):
            self._data_source_manager.default_data_source = default_ds
            elems = self.get_elements()
            for elem in elems:
                elem._data_source_manager.default_data_source = default_ds
        elif default_ds is not None:
            raise DataSourceException("{0} is not a data source. Please enter "
                                      "{1} or {2}.".format(default_ds,
                                                           pytac.LIVE,
                                                           pytac.SIM))

    def get_default_units(self):
        """Get the default unit type, pytac.ENG or pytac.PHYS.

        Returns:
            str: the default unit type for the entire lattice.
        """
        return self._data_source_manager.default_units

    def get_default_data_source(self):
        """Get the default data source, pytac.LIVE or pytac.SIM.

        Returns:
            str: the default data source for the entire lattice.
        """
        return self._data_source_manager.default_data_source

    def convert_family_values(self, family, field, values, origin, target):
        """Convert the given values according to the given origin and target
        units, using the unit conversion objects for the given field on the
        elements in the given family.

        Args:
            family (str): the family of elements which the values belong to.
            field (str): the field on the elements which the values are from.
            values (sequence): values to be converted.
            origin (str): pytac.ENG or pytac.PHYS.
            target (str): pytac.ENG or pytac.PHYS.
        """
        elements = self.get_elements(family)
        if len(elements) != len(values):
            raise IndexError("Number of elements in given sequence({0}) must "
                             "be equal to the number of elements in the "
                             "family({1}).".format(len(values), len(elements)))
        converted_values = []
        for elem, value in zip(elements, values):
            uc = elem.get_unitconv(field)
            converted_values.append(uc.convert(value, origin, target))
        return converted_values


class EpicsLattice(Lattice):
    """EPICS-aware lattice class.

    Allows efficient get_values() and set_values() methods, and adds
    get_pv_names() method.

    **Attributes:**

    Attributes:
        name (str): The name of the lattice.
        symmetry (int): The symmetry of the lattice (the number of cells).

    .. Private Attributes:
           _elements (list): The list of all the element objects in the lattice
           _cs (ControlSystem): The control system to use for the more
                                 efficient batch getting and setting of PVs.
           _data_source_manager (DataSourceManager): A class that manages the
                                                      data sources associated
                                                      with this lattice.
    """
    def __init__(self, name, epics_cs, symmetry=None):
        """
        Args:
            name (str): The name of the epics lattice.
            epics_cs (ControlSystem): The control system used to store the
                                       values on a PV.
            symmetry (int): The symmetry of the lattice (the number of cells).

        **Methods:**
        """
        super(EpicsLattice, self).__init__(name, symmetry)
        self._cs = epics_cs

    def get_pv_name(self, field, handle):
        """Get the PV name for a specific field, and handle on this lattice.

        Args:
            field (str): The requested field.
            handle (str): pytac.RB or pytac.SP.

        Returns:
            str: The readback or setpoint PV for the specified field.
        """
        try:
            return (self._data_source_manager._data_sources[pytac.LIVE]
                    .get_device(field).get_pv_name(handle))
        except KeyError:
            raise DataSourceException("Lattice {0} has no device for field "
                                      "{1}.".format(self, field))
        except AttributeError:
            raise DataSourceException("Cannot get PV for field {0} on lattice "
                                      "{1}, as basic devices do not have "
                                      "associated PV's.".format(field, self))

    def get_element_pv_names(self, family, field, handle):
        """Get the PV names for the given field, and handle, on all elements
        in the given family in the lattice.

        Assume that the elements are EpicsElements that have the get_pv_name()
        method.

        Args:
            family (str): The requested family.
            field (str): The requested field.
            handle (str): pytac.RB or pytac.SP.

        Returns:
            list: A list of PV names, strings.
        """
        elements = self.get_elements(family)
        pv_names = []
        for element in elements:
            pv_names.append(element.get_pv_name(field, handle))
        return pv_names

    def get_element_values(self, family, field, handle=pytac.RB,
                           units=pytac.DEFAULT, data_source=pytac.DEFAULT,
                           throw=True, dtype=None):
        """Get the value of the given field for all elements in the given
        family in the lattice.

        Args:
            family (str): family of elements to request the values of.
            field (str): field to request values for.
            handle (str): pytac.RB or pytac.SP.
            units (str): pytac.ENG or pytac.PHYS.
            data_source (str): pytac.LIVE or pytac.SIM.
            throw (bool): On failure: if True, raise ControlSystemException; if
                           False, None will be returned for any PV that fails
                           and a warning will be logged.
            dtype (numpy.dtype): if None, return a list. If not None, return a
                                  numpy array of the specified type.

        Returns:
            list or numpy.array: The requested values.
        """
        if data_source == pytac.DEFAULT:
            data_source = self.get_default_data_source()
        if units == pytac.DEFAULT:
            units = self.get_default_units()
        if data_source == pytac.LIVE:
            pv_names = self.get_element_pv_names(family, field, handle)
            values = self._cs.get_multiple(pv_names, throw)
            if units == pytac.PHYS:
                values = self.convert_family_values(family, field, values,
                                                    pytac.ENG, pytac.PHYS)
        else:
            values = super(EpicsLattice, self).get_element_values(family,
                                                                  field,
                                                                  handle,
                                                                  units,
                                                                  data_source,
                                                                  throw)
        if dtype is not None:
            values = numpy.array(values, dtype=dtype)
        return values

    def set_element_values(self, family, field, values, handle=pytac.SP,
                           units=pytac.DEFAULT, data_source=pytac.DEFAULT,
                           throw=True):
        """Set the value of the given field for all elements in the given
        family in the lattice to the given values.

        Args:
            family (str): family of elements on which to set values.
            field (str):  field to set values for.
            values (sequence): A list of values to assign.
            handle (str): pytac.SP or pytac.RB.
            units (str): pytac.ENG or pytac.PHYS.
            data_source (str): pytac.LIVE or pytac.SIM.
            throw (bool): On failure: if True, raise ControlSystemException: if
                           False, log a warning.

        Raises:
            IndexError: if the given list of values doesn't match the number of
                         elements in the family.
        """
        if data_source == pytac.DEFAULT:
            data_source = self.get_default_data_source()
        if units == pytac.DEFAULT:
            units = self.get_default_units()
        if handle != pytac.SP:
            raise HandleException("Must write using {0}.".format(pytac.SP))
        if data_source == pytac.LIVE:
            if units == pytac.PHYS:
                values = self.convert_family_values(family, field, values,
                                                    pytac.PHYS, pytac.ENG)
            pv_names = self.get_element_pv_names(family, field, pytac.SP)
            if len(pv_names) != len(values):
                raise IndexError("Number of elements in given sequence({0}) "
                                 "must be equal to the number of elements in "
                                 "the family({1}).".format(len(values),
                                                           len(pv_names)))
            self._cs.set_multiple(pv_names, values, throw)
        else:
            super(EpicsLattice, self).set_element_values(family, field, values,
                                                         pytac.SP, units,
                                                         data_source, throw)
