"""Module containing the element class."""
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Sequence, Set, cast

import pytac
from pytac.cs import AugmentedType
from pytac.data_source import DataSourceManager, DeviceDataSource
from pytac.device import Device
from pytac.exceptions import DataSourceException, FieldException
from pytac.units import UnitConv

if TYPE_CHECKING:
    from pytac.lattice import Lattice


class Element(object):
    """Class representing one physical element in an accelerator lattice.

    An element has zero or more devices (e.g. quadrupole magnet) associated
    with each of its fields (e.g. 'b1' for a quadrupole).
    """

    name: Optional[str]
    """The name identifying the element. The user is free to define this for their
        own purposes."""
    type_: str
    """The type of the element. The user is free to define this for their own
        purposes."""
    length: float
    """The length of the element in metres."""

    _lattice: Optional["Lattice"]
    """The lattice to which the element belongs."""
    _data_source_manager: DataSourceManager
    """A class that manages the data sources associated with this element."""
    _families: Set[Any]
    """The families this element is a member of, stored as lowercase strings."""

    def __init__(
        self,
        length: float,
        element_type: str,
        name: Optional[str] = None,
        lattice: Optional["Lattice"] = None,
    ) -> None:
        """Initialise the Element object.

        Args:
            length: The length of the element.
            element_type: The type of the element.
            name: The unique identifier for the element in the ring.
            lattice: The lattice to which the element belongs.
        """
        self.name = name
        self.type_ = element_type
        self.length = length
        # Families are case insensitive but stored in lowercase.
        self._families = set()
        self._lattice = lattice
        self._data_source_manager = DataSourceManager()

    @property
    def index(self) -> Optional[int]:
        """The element's index within the ring, starting at 1."""
        if self._lattice is None:
            return None
        else:
            return self._lattice._elements.index(self) + 1

    @property
    def s(self) -> Optional[float]:
        """The element's start position within the lattice in metres."""
        if self._lattice is None:
            return None
        else:
            # index is not None when self._lattice is not None as per index property.
            index = cast(int, self.index)
            # Lattice must be iterable and indexable, however mypy doesnt accept only
            # having __getitem__ and __len__ instead of __iter__.
            typed_lattice = cast(Sequence, self._lattice)
            return sum([el.length for el in typed_lattice[: index - 1]])

    @property
    def cell(self) -> Optional[int]:
        """The lattice cell this element is within.

        N.B. If the element spans multiple cells then the cell it begins in is
        returned (lowest cell number).
        """
        if self._lattice is None:
            return None
        elif self._lattice.cell_length is None:
            return None
        else:
            # s is not None when self._lattice is not None as per s property.
            s = cast(float, self.s)
            return int(s / self._lattice.cell_length) + 1

    @property
    def families(self) -> Set[Any]:
        """set(str): All families that this element is in."""
        return set(self._families)

    def __str__(self) -> str:
        """Return a representation of an element, as a string.

        Returns:
            A representation of an element.
        """
        repn = "<Element "
        if self.name is not None:
            repn += "'{0}', ".format(self.name)
        if self.index is not None:
            repn += "index {0}, ".format(self.index)
        repn += "length {0} m, ".format(self.length)
        if self.cell is not None:
            repn += "cell {0}, ".format(self.cell)
        repn += "families {0}>".format(", ".join(f for f in self.families))
        return repn

    __repr__ = __str__

    def set_default_data_source(self, data_source_type: str) -> None:
        """Set the default data source for this element.

        Args:
            data_source_type: the type of the data source being set:
                              pytac.LIVE or pytac.SIM.
        """
        self._data_source_manager.default_data_source = data_source_type

    def set_default_units(self, units: str) -> None:
        """Set the default units type for this element.

        Args:
            units: pytac.PHYS or pytac.ENG
        """
        self._data_source_manager.default_units = units

    def set_data_source(
        self, data_source: DeviceDataSource, data_source_type: str
    ) -> None:
        """Add a data source to the element.

        Args:
            data_source: the data source to be set.
            data_source: the type of the data source being set:
                         pytac.LIVE or pytac.SIM.
        """
        self._data_source_manager.set_data_source(data_source, data_source_type)

    def get_fields(self) -> Dict[str, Iterable]:
        """Get the all fields defined on an element.

        Includes all fields defined by all data sources.

        Returns:
            A dictionary of all the fields defined on an element,
                   separated by data source(key).
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
        try:
            self._data_source_manager.add_device(field, device, uc)
        except DataSourceException as e:
            raise DataSourceException(f"{self}: {e}.")

    def get_device(self, field: str) -> Device:
        """Get the device for the given field.

        A DeviceDataSource must be set before calling this method, this
        defaults to pytac.LIVE as that is the only data source that currently
        uses devices.

        Args:
            field: The lookup key to find the device on an element.

        Returns:
            The device on the given field.

        Raises:
            DataSourceException: if no DeviceDataSource is set.
        """
        try:
            return self._data_source_manager.get_device(field)
        except DataSourceException as e:
            raise DataSourceException(f"{self}: {e}.")

    def get_unitconv(self, field: str) -> UnitConv:
        """Get the unit conversion option for the specified field.

        Args:
            field: The field associated with this conversion.

        Returns:
            The object associated with the specified field.

        Raises:
            FieldException: if no unit conversion object is present.
        """
        try:
            return self._data_source_manager.get_unitconv(field)
        except FieldException as e:
            raise FieldException(f"{self}: {e}")

    def set_unitconv(self, field: str, uc: UnitConv) -> None:
        """Set the unit conversion option for the specified field.

        Args:
            field: The field associated with this conversion.
            uc: The unit conversion object to be set.
        """
        self._data_source_manager.set_unitconv(field, uc)

    def add_to_family(self, family: str) -> None:
        """Add the element to the specified family.

        Args:
            family: Represents the name of the family.
        """
        self._families.add(family.lower())

    def is_in_family(self, family: str) -> bool:
        """Return true if the element is in the specified family.

        Args:
            family: Family to check.

        Returns:
            true if element is in the specified family.
        """
        return family.lower() in self._families

    def get_value(
        self,
        field: str,
        handle: str = pytac.RB,
        units: str = pytac.DEFAULT,
        data_source: str = pytac.DEFAULT,
        throw: bool = True,
    ) -> Optional[AugmentedType]:
        """Get the value for a field.

        Returns the value of a field on the element. This value is uniquely
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
            FieldException: if the element does not have the specified field.
        """
        try:
            return self._data_source_manager.get_value(
                field, handle, units, data_source, throw
            )
        except DataSourceException as e:
            raise DataSourceException(f"{self}: {e}")
        except FieldException as e:
            raise FieldException(f"{self}: {e}")

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
            FieldException: if the element does not have the specified field.
        """
        try:
            self._data_source_manager.set_value(field, value, units, data_source, throw)
        except DataSourceException as e:
            raise DataSourceException(f"{self}: {e}")
        except FieldException as e:
            raise FieldException(f"{self}: {e}")

    def set_lattice(self, lattice: "Lattice") -> None:
        """Set the stored lattice reference for this element to the passed
        lattice object.

        Args:
            lattice: lattice object to store a reference to.
        """
        self._lattice = lattice


class EpicsElement(Element):
    """EPICS-aware element.

    Adds get_pv_name() method.
    """

    def get_pv_name(self, field: str, handle: str) -> str:
        """Get PV name for the specified field and handle.

        Args:
            field: The requested field.
            handle: pytac.RB or pytac.SP.

        Returns:
            The readback or setpoint PV for the specified field.

        Raises:
            DataSourceException: if there is no data source for this field.
            FieldException: if the specified field doesn't exist.
        """
        try:
            return (
                self._data_source_manager.get_data_source(pytac.LIVE)
                .get_device(field)
                .get_pv_name(handle)
            )
        except DataSourceException as e:
            raise DataSourceException(f"{self}: {e}")
        except AttributeError:
            raise DataSourceException(
                f"Cannot get PV for field {field} on element "
                f"{self}, as the device does not have associated PVs."
            )
        except FieldException as e:
            raise FieldException(f"{self}: {e}")
