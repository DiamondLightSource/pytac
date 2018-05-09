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
        self._uc = {}
        self._models = {}

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
        """Add a model to the element.

        Args:
            model (Model): instance of Model
            model_type (str): pytac.LIVE or pytac.SIM

        """
        self._models[model_type] = model

    def get_fields(self):
        """Get the fields defined on an element.

        Includes all fields defined by all models.

        Returns:
            list: A sequence of all the fields defined on an element.
        """
        fields = set()
        for model in self._models:
            fields.update(self._models[model].get_fields())
        return fields

    def add_device(self, field, device, uc):
        """Add device and unit conversion objects to a given field.

        A DeviceModel must be set before calling this method.

        Args:
            field (str): The key to store the unit conversion and device
                objects.
            device (Device): device object used for this field.
            uc (UnitConv): unit conversion object used for this field.

        Raises:
            KeyError if no DeviceModel is set

        """
        self._models[pytac.LIVE].add_device(field, device)
        self._uc[field] = uc

    def get_device(self, field):
        """Get the device for the given field.

        A DeviceModel must be set before calling this method.

        Args:
            field (str): The lookup key to find the device on an element.

        Returns:
            Device: The device on the given field.

        Raises:
            KeyError if no DeviceModel is set
        """
        return self._models[pytac.LIVE].get_device(field)

    def get_unitconv(self, field):
        """Get the unit conversion option for the specified field.

        Args:
            field (str): Field associated with this conversion

        Returns:
            UnitConv object associated with the specified field

        Raises:
            KeyError if no unit conversion object is present.

        """
        return self._uc[field]

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
            field (str): requested field
            handle (str): pytac.SP or pytac.RB
            unit (str): pytac.ENG or pytac.PHYS
                returned.
            model (str): pytac.LIVE or pytac.SIM

        Returns:
            Number: value of the requested field

        Raises:
            DeviceException if there is no device on the given field
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
            field (str): requested field
            value (float): value to set
            unit (str): pytac.ENG or pytac.PHYS
            model (str): pytac.LIVE or pytac.SIM

        Raises:
            DeviceException if arguments are incorrect
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

        Args:
            field (str): requested field
            handle (str): pytac.RB or pytac.SP

        Returns:
            str: readback or setpoint pv for the specified field

        Raises:
            DeviceException if there is no device for this field
        """
        try:
            return self._models[pytac.LIVE].get_pv_name(field, handle)
        except KeyError:
            raise DeviceException('{} has no device for field {}'.format(self, field))

    def get_cs(self, field):
        return self._devices[field].get_cs()
