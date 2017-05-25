from pytac.exceptions import PvException
import pytac


class Element(object):
    def __init__(self, name, length, element_type):
        """An element of the ring.

        Represents an element of the lattice. Contains a family set
        that should contain the families the element is part of. There
        exist unit conversion and devices dictionaries that need to be
        updated accordingly. The element is enabled by default.

        Args:
            name (int): Unique identifier for the element in the ring.
            length (float): The length of the element.
            element_type (string): Type of the element.

        """
        self._name = name
        self._type = element_type
        self._length = length
        self.families = set()
        self._uc = dict()
        self._devices = dict()

    def __str__(self):
        """Auxiliary function to print out an element.

        Return a representation of an element, as a string.

        Returns:
            string: A representation of an element.
        """
        return 'Element: {0}, length: {1}, families: {2}'.format(self._name, self._length, self.families)

    def get_fields(self):
        """Get the fields defined on an element.

        Returns:
            list: A sequence of all the fields defined on an element.
        """
        return self._devices.keys()

    def get_length(self):
        """Gets the length of an element.

        Returns:
            float: A floating point number that represents the length
            of the element.
        """

        return self._length

    def add_device(self, field, device, uc):
        """Add device and unit conversion objects to a given field.

        Args:
            field (string): The key to store the unit conversion and device
                objects.
            device (Device): Represents a device stored on an element.
            uc (PolyUnitConv/PchipUnitConv): Represents a unit conversion object stored for a
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
        """
        return self._devices[field]

    def add_to_family(self, family):
        """Add the element to the specified family.

        Args:
            family (string): Represents the name of the family
        """
        self.families.add(family)

    def get_pv_value(self, field, handle, unit=pytac.ENG, sim=False):
        """Get the value of a pv.

        Returns the value of a pv on the element. This value is uniquely
        identified by a field and a handle. The returned value is either
        in engineering or physics units. The sim flag returns either real
        or simulated values.

        Args:
            field (string): Choose which device to use.
            handle (string): Can take as value either 'setpoint' or 'readback'.
            unit (string): Specify either engineering or physics units to be
                returned.
            sim (boolean): Set whether real or simulated values to be returned.

        Returns:
            Number: A number that corresponds to the pv value of the identified
            device.

        Raises:
            PvException: When there is no associated device on the given field.
        """
        if not sim:
            if field in self._devices:
                value = self._devices[field].get_value(handle)
                if unit == pytac.PHYS:
                    value = self._uc[field].eng_to_phys(value)
                return value
            else:
                raise PvException("No device associated with field {0}".format(field))
        else:
            value = self._physics.get_value(field, handle, unit)
            if unit == pytac.ENG:
                value = self._uc[field].eng_to_phys(value)
            return value

    def put_pv_value(self, field, value, unit=pytac.ENG, sim=False):
        """Set the pv value on a uniquely identified device.

        This value can be set on the machine or the simulation.
        A field is required to identify a device. Returned value
        can be engineering or physics.

        Args:
            field (string): The key used to identify a device.
            value (float): The value set on the device.
            unit (string): Can be engineering or physics units.
            sim (boolean): To set whether the simulation is on or off.

        Raises:
            PvException: An exception occured accessing a field with
            no associated device.
        """
        if not sim:
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
            self._physics.put_value(field, value)

    def get_pv_name(self, field, handle='*'):
        """ Get a pv name on a device.

        Can return the readback and setpoint pvs if no handle is specified.

        Args:
            field (string): Uniquely identifies a device.
            handle(string): Can be 'readback' or 'setpoint' to return each pv.
                If neither is specified then both pvs are returned.

        Returns:
            string: A readback or setpoint pv associated with the identified device.

        Raises:
            PvException: An exception occured accessing a field with
            no associated device.
        """
        try:
            return self._devices[field].get_pv_name(handle)
        except KeyError:
            raise PvException('Element has no device for field {}'.format(field))

    def get_cs(self, field):
        return self._devices[field].get_cs()
