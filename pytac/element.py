"""Module containing the element class."""

from pytac.exceptions import PvException
import pytac


class Element(object):
    """Class representing one physical element in an accelerator lattice.

    An element has zero or more devices (e.g. quadrupole magnet) associated
    with a field ('b1' for a quadrupole).

    Attributes:
        name (str): name identifying the element
        type_ (str): type of the element
        length (number): length of the element in metres
        s (float): the element's start position within the lattice in metres
        cell (int): the element's cell within the lattice
        families (set): the families this element is a member of

    """
    def __init__(self, name, length, element_type, s=None, cell=None):
        """
        Args:
            name (int): Unique identifier for the element in the ring.
            length (float): The length of the element.
            element_type (string): Type of the element.
            s (float): Position of the start of the element in the ring
            cell (int): lattice cell this element is wihin

        """
        self.name = name
        self.type_ = element_type
        self.length = length
        self.s = s
        self.cell = cell
        self.families = set()
        self._uc = dict()
        self._devices = dict()
        self._model = None

    def __str__(self):
        """Auxiliary function to print out an element.

        Return a representation of an element, as a string.

        Returns:
            string: A representation of an element.
        """
        repn = '<Element {0}, length {1} m, families {2}>'
        return repn.format(self.name,
                           self.length,
                           ', '.join(f for f in self.families))

    __repr__ = __str__

    def set_model(self, model):
        self._model = model

    def get_fields(self):
        """Get the fields defined on an element.

        Returns:
            list: A sequence of all the fields defined on an element.
        """
        return self._devices.keys()

    def add_device(self, field, device, uc):
        """Add device and unit conversion objects to a given field.

        Args:
            field (string): The key to store the unit conversion and device
                objects.
            device (Device): Represents a device stored on an element.
            uc (UnitConv): Represents a unit conversion object used for this
                device.
        """
        self._devices[field] = device
        self._uc[field] = uc

    def get_device(self, field):
        """Get the device for the given field.

        Args:
            field (string): The lookup key to find the device on an element.

        Returns:
            Device: The device on the given field.

        Raises:
            KeyError if no such device exists
        """
        return self._devices[field]

    def add_to_family(self, family):
        """Add the element to the specified family.

        Args:
            family (string): Represents the name of the family
        """
        self.families.add(family)

    def get_value(self, field, handle, unit=pytac.ENG, model=pytac.LIVE):
        """Get the value for a field.

        Returns the value for a field on the element. This value is uniquely
        identified by a field and a handle. The returned value is either
        in engineering or physics units. The model flag returns either real
        or simulated values.

        Args:
            field (string): Choose which device to use.
            handle (string): Can take as value either 'setpoint' or 'readback'.
            unit (string): Specify either engineering or physics units to be
                returned.
            model (string): Set whether real or simulated values to be returned.

        Returns:
            Number: A number that corresponds to the value of the identified
            field.

        Raises:
            PvException: When there is no associated device on the given field.
        """
        if model == pytac.LIVE:
            if field in self._devices:
                value = self._devices[field].get_value(handle)
                if unit == pytac.PHYS:
                    value = self._uc[field].eng_to_phys(value)
                return value
            else:
                raise PvException("No device associated with field {0}".format(field))
        else:
            value = self._model.get_value(field)
            if unit == pytac.ENG:
                value = self._uc[field].phys_to_eng(value)
            return value

    def set_value(self, field, value, unit=pytac.ENG, model=pytac.LIVE):
        """Set the value on a uniquely identified device.

        This value can be set on the machine or the simulation.
        A field is required to identify a device. Returned value
        can be engineering or physics.

        Args:
            field (string): The key used to identify a device.
            value (float): The value set on the device.
            unit (string): Can be engineering or physics units.
            model (string): The type of model: simulation or live

        Raises:
            PvException: An exception occured accessing a field with
            no associated device.
        """
        if model == pytac.LIVE:
            if field in self._devices:
                if unit == pytac.PHYS:
                    value = self._uc[field].phys_to_eng(value)
                self._devices[field].put_value(value)
            else:
                raise PvException('''There is no device associated with
                                     field {0}'''.format(field))
        else:
            if unit == pytac.ENG:
                value = self._uc[field].eng_to_phys(value)
            self._model.set_value(field, value)

    def get_pv_name(self, field, handle):
        """ Get a pv name on a device.

        Can return the readback and setpoint pvs if no handle is specified.

        Args:
            field (string): Uniquely identifies a device.
            handle(string): pytac.RB or pytac.SP

        Returns:
            string: A readback or setpoint pv associated with the identified device.

        Raises:
            PvException: An exception occured accessing a field with
            no associated device.
        """
        try:
            return self._devices[field].get_pv_name(handle)
        except KeyError:
            raise PvException('{} has no device for field {}'.format(self, field))

    def get_cs(self, field):
        return self._devices[field].get_cs()
