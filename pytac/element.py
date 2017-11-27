"""Module containing the element class."""
import pytac
from pytac.device import DeviceException


class Element(object):
    """Class representing one physical element in an accelerator lattice.

    An element has zero or more devices (e.g. quadrupole magnet) associated
    with a field ('b1' for a quadrupole).

    Attributes:
        name (str): name identifying the element
        type_ (str): type of the element
        length (number): length of the element in metres
        s (float): the element's start position within the lattice in metres
        index (int): the element's index within the ring, starting at 1
        cell (int): the element's cell within the lattice
        families (set): the families this element is a member of

    """
    def __init__(self, name, length, element_type,
                 s=None, index=None, cell=None):
        """
        Args:
            name (int): Unique identifier for the element in the ring.
            length (float): The length of the element.
            element_type (str): Type of the element.
            s (float): Position of the start of the element in the ring
            index (float): Index of the element in the ring, starting at 1
            cell (int): lattice cell this element is wihin

        """
        self.name = name
        self.type_ = element_type
        self.length = length
        self.s = s
        self.index = index
        self.cell = cell
        self.families = set()
        self._uc = dict()
        self._models = {pytac.LIVE: None, pytac.SIM: None}

    def __str__(self):
        """Auxiliary function to print out an element.

        Return a representation of an element, as a string.

        Returns:
            str: A representation of an element.
        """
        repn = '<Element {0}, length {1} m, families {2}>'
        return repn.format(self.name,
                           self.length,
                           ', '.join(f for f in self.families))

    __repr__ = __str__

    def set_model(self, model, model_type):
        self._models[model_type] = model

    def get_fields(self):
        """Get the fields defined on an element.

        Returns:
            list: A sequence of all the fields defined on an element.
        """
        return self._models[pytac.LIVE].get_fields()

    def add_device(self, field, device, uc):
        """Add device and unit conversion objects to a given field.

        Args:
            field (str): The key to store the unit conversion and device
                objects.
            device (Device): Represents a device stored on an element.
            uc (UnitConv): Represents a unit conversion object used for this
                device.
        """
        self._models[pytac.LIVE].add_device(field, device)
        self._uc[field] = uc

    def get_device(self, field):
        """Get the device for the given field.

        Args:
            field (str): The lookup key to find the device on an element.

        Returns:
            Device: The device on the given field.

        Raises:
            KeyError if no such device exists
        """
        val = self._models[pytac.LIVE].get_device(field)
        print('returning {}'.format(val))
        return val

    def add_to_family(self, family):
        """Add the element to the specified family.

        Args:
            family (str): Represents the name of the family
        """
        self.families.add(family)

    def get_value(self, field, handle=pytac.RB, units=pytac.ENG, model=pytac.LIVE):
        """Get the value for a field.

        Returns the value for a field on the element. This value is uniquely
        identified by a field and a handle. The returned value is either
        in engineering or physics units. The model flag returns either real
        or simulated values.

        Args:
            field (str): Choose which device to use.
            handle (str): Can take as value either 'setpoint' or 'readback'.
            unit (str): Specify either engineering or physics units to be
                returned.
            model (str): Set whether real or simulated values to be returned.

        Returns:
            Number: A number that corresponds to the value of the identified
            field.

        Raises:
            DeviceException: When there is no associated device on the given field.
        """
        try:
            model = self._models[model]
            value = model.get_value(field, handle)
            return self._uc[field].convert(value, origin=model.units, target=units)
        except KeyError:
            raise DeviceException('No model type {} on element {}'.format(model,
                self))

    def set_value(self, field, value, handle=pytac.SP, units=pytac.ENG, model=pytac.LIVE):
        """Set the value on a uniquely identified device.

        This value can be set on the machine or the simulation.
        A field is required to identify a device. Returned value
        can be engineering or physics.

        Args:
            field (str): The key used to identify a device.
            value (float): The value set on the device.
            unit (str): Can be engineering or physics units.
            model (str): The type of model: simulation or live

        Raises:
            DeviceException: An exception occured accessing a field with
            no associated device.
        """
        if handle != pytac.SP:
            raise DeviceException('Must write using {}'.format(pytac.SP))
        try:
            model = self._models[model]
            self._uc[field].convert(origin=units, target=model.units)
            model.set_value(field, value)
        except KeyError:
            raise DeviceException('No model type {} on element {}'.format(model,
                self))

    def get_pv_name(self, field, handle):
        """ Get a pv name on a device.

        Can return the readback and setpoint pvs if no handle is specified.

        Args:
            field (str): Uniquely identifies a device.
            handle (str): pytac.RB or pytac.SP

        Returns:
            str: A readback or setpoint pv associated with the identified device.

        Raises:
            DeviceException: An exception occured accessing a field with
            no associated device.
        """
        try:
            return self._models[pytac.LIVE].get_pv_name(field, handle)
        except KeyError:
            raise DeviceException('{} has no device for field {}'.format(self, field))

    def get_cs(self, field):
        return self._devices[field].get_cs()
