"""Module containing the element class."""
import pytac
from pytac.data_source import DataSourceManager
from pytac.exceptions import DataSourceException, FieldException


class Element(object):
    """Class representing one physical element in an accelerator lattice.

    An element has zero or more devices (e.g. quadrupole magnet) associated
    with each of its fields (e.g. 'b1' for a quadrupole).

    **Attributes:**

    Attributes:
        name (str): The name identifying the element.
        type_ (str): The type of the element.
        length (float): The length of the element in metres.
        s (float): The element's start position within the lattice in metres.
        index (int): The element's index within the ring, starting at 1.
        cell (int): The lattice cell this element is wihin.
        families (set): The families this element is a member of.

    .. Private Attributes:
           _data_source_manager (DataSourceManager): A class that manages the
                                                      data sources associated
                                                      with this element.
    """
    def __init__(self, name, length, element_type, s, index=None, cell=None):
        """
        Args:
            name (int): The unique identifier for the element in the ring.
            length (float): The length of the element.
            element_type (str): The type of the element.
            s (float): The position of the start of the element in the ring.
            index (float): The index of the element in the ring, starting at 1.
            cell (int): The lattice cell this element is wihin.

        **Methods:**
        """
        self.name = name
        self.type_ = element_type
        self.length = length
        self.s = s
        self.index = index
        self.cell = cell
        self.families = set()
        self._data_source_manager = DataSourceManager()

    def __str__(self):
        """Auxiliary function to print out an element.

        Return a representation of an element, as a string.

        Returns:
            str: A representation of an element.
        """
        repn = '<Element {0}, length {1} m, families {2}>'
        return repn.format(self.name, self.length, ', '.join(f for f in
                                                             self.families))

    __repr__ = __str__

    def set_data_source(self, data_source, data_source_type):
        """Add a data source to the element.

        Args:
            data_source (DataSource): the data source to be set.
            data_source_type (str): the type of the data source being set
                                     pytac.LIVE or pytac.SIM.
        """
        self._data_source_manager.set_data_source(data_source, data_source_type)

    def get_fields(self):
        """Get the all fields defined on an element.

        Includes all fields defined by all data sources.

        Returns:
            dict: A dictionary of all the fields defined on an element,
                   separated by data source(key).
        """
        return self._data_source_manager.get_fields()

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
            DataSourceException: if no DeviceDataSource is set.
        """
        try:
            self._data_source_manager.add_device(field, device, uc)
        except DataSourceException:
            raise DataSourceException("No device data source for field {0} on "
                                      "element {1}.".format(field, self))

    def get_device(self, field):
        """Get the device for the given field.

        A DeviceDataSource must be set before calling this method, this defaults
        to pytac.LIVE as that is the only DeviceDataSource currently.

        Args:
            field (str): The lookup key to find the device on an element.

        Returns:
            Device: The device on the given field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        try:
            return self._data_source_manager.get_device(field)
        except DataSourceException:
            raise DataSourceException("No device data source for field {0} on "
                                      "element {1}.".format(field, self))

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
                                 "element {1}.".format(field, self))

    def add_to_family(self, family):
        """Add the element to the specified family.

        Args:
            family (str): Represents the name of the family.
        """
        self.families.add(family)

    def get_value(self, field, handle=pytac.RB, units=pytac.DEFAULT,
                  data_source=pytac.DEFAULT):
        """Get the value for a field.

        Returns the value of a field on the element. This value is uniquely
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
            DataSourceException: if there is no data source on the given field.
            FieldException: if the element does not have the specified field.
        """
        try:
            return self._data_source_manager.get_value(field, handle, units,
                                                       data_source)
        except DataSourceException:
            raise DataSourceException("No data source {0} on element {1}."
                                      .format(data_source, self))
        except FieldException:
            raise FieldException("Element {0} does not have field {1}."
                                 .format(self, field))

    def set_value(self, field, value, handle=pytac.SP, units=pytac.DEFAULT,
                  data_source=pytac.DEFAULT):
        """Set the value for a field.

        This value can be set on the machine or the simulation.

        Args:
            field (str): The requested field.
            value (float): The value to set.
            handle (str): pytac.SP or pytac.RB.
            units (str): pytac.ENG or pytac.PHYS.
            data_source (str): pytac.LIVE or pytac.SIM.

        Raises:
            DataSourceException: if arguments are incorrect.
            FieldException: if the element does not have the specified field.
        """
        try:
            self._data_source_manager.set_value(field, value, handle, units,
                                                data_source)
        except DataSourceException:
            raise DataSourceException("No data source {0} on element {1}."
                                      .format(data_source, self))
        except FieldException:
            raise FieldException("Element {0} does not have field {1}."
                                 .format(self, field))
