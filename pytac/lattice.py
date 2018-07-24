""" Representation of a lattice object which contains all the elements of the machine."""
import numpy


class LatticeException(Exception):
    pass


class Lattice(object):
    """Representation of a lattice.

    Represents a lattice object that contains all elements of the ring. It has
    a name and a control system to be used for unit conversion.

    **Attributes:**

    Attributes:
        name (str): The name of the lattice.

    .. Private Attributes:
           _lattice (list): The list of all the element objects in the lattice.
           _cs (ControlSystem): The control system used to store the values on
                                 a pv.
           _energy (int): The total energy of the lattice.
           _model (Model): A pytac model object associated with the lattice.
    """

    def __init__(self, name, control_system, energy):
        """
        Args:
            name (str): The name of the lattice.
            control_system (ControlSystem): The control system used to store
                                             the values on a pv.
            energy (int): The total energy of the lattice.
        """
        self.name = name
        self._lattice = []
        self._cs = control_system
        self._energy = energy
        self._model = None

    def set_model(self, model):
        """Sets the pytac model object associated with the lattice.

        Returns:
            Model: A pytac model object associated with the lattice.
        """
        self._model = model

    def get_energy(self):
        """Function to get the total energy of the lattice.

        Returns:
            int: energy of the lattice
        """
        return self._energy

    def __getitem__(self, n):
        """Get the (n + 1)th element of the lattice - i.e. index 0 represents
        the first element in the lattice.

        Args:
            n (int): index

        Returns:
            Element: indexed element
        """

        return self._lattice[n]

    def __len__(self):
        """The number of elements in the lattice.

        When using the len function returns the number of elements in
        the lattice.

        Returns:
            int: The number of elements in the lattice.
        """
        return len(self._lattice)

    def get_length(self):
        """Returns the length of the lattice.

        Returns:
            float: The length of the lattice.
        """
        total_length = 0
        for e in self._lattice:
            total_length += e.length
        return total_length

    def add_element(self, element):
        """Append an element to the lattice.

        Args:
            element (Element): element to append
        """
        self._lattice.append(element)

    def get_elements(self, family=None, cell=None):
        """Get the elements of a family from the lattice.

        If no family is specified it returns all elements.

        Elements are returned in the order they exist in the ring.

        Args:
            family (str): requested family
            cell (int): restrict elements to those in the specified cell

        Returns:
            list(Element): list containing all elements of the specified family
        """
        elements = []
        if family is None:
            elements = self._lattice

        for element in self._lattice:
            if family in element.families:
                elements.append(element)

        if cell is not None:
            elements = [e for e in elements if e.cell == cell]

        return elements

    def get_all_families(self):
        """Get all families of elements in the lattice

        Returns:
            set(str): all defined families

        """
        families = set()
        for element in self._lattice:
            families.update(element.families)

        return families

    def get_pv_names(self, family, field, handle):
        """Get all pv names for a specific family, field and handle.

        Args:
            family (str): requested family
            field (str): requested field
            handle (str): pytac.RB or pytac.SP

        Returns:
            list(str): list of pv names
        """
        elements = self.get_elements(family)
        pv_names = []
        for element in elements:
            pv_names.append(element.get_pv_name(field, handle))
        return pv_names

    def get_values(self, family, field, handle, dtype=None):
        """Get all values for a family and field.

        Args:
            family (str): family to request the values of
            field (str): field to request values for
            handle (str): pytac.RB or pytac.SP
            dtype (numpy.dtype): if None, return a list. If not None,
                return a numpy array of the specified type.

        Returns:
            list or numpy array: sequence of values
        """
        pv_names = self.get_pv_names(family, field, handle)
        values = self._cs.get(pv_names)
        if dtype is not None:
            values = numpy.array(values, dtype=dtype)
        return values

    def set_values(self, family, field, values):
        """Sets the values for a family and field.

        The pvs are determined by family and device. Note that only setpoint
        pvs can be modified.

        Args:
            family (str): family on which to set values
            field (str):  field to set values for
            values (sequence): A list of values to assign

        Raises:
            LatticeException: if the given list of values doesn't match the
                number of elements in the family
        """
        pv_names = self.get_pv_names(family, field, 'setpoint')
        if len(pv_names) != len(values):
            raise LatticeException("Number of elements in given array must be "
                    "equal to the number of elements in the lattice")
        self._cs.put(pv_names, values)

    def get_s(self, elem):
        """Find the s position of an element in the lattice.

        Note that the given element must exist in the lattice.

        Args:
            elem (Element): The element that the position is being asked for.

        Returns:
            float: the position of the given element.

        Raises
            LatticeException: if element doesn't exist in the lattice.
        """
        s_pos = 0
        for el in self._lattice:
            if el is not elem:
                s_pos += el.length
            else:
                return s_pos
        raise LatticeException(
                'Element {} not in lattice {}'.format(elem, self)
        )

    def get_family_s(self, family):
        """Get s positions for all elements from the same family.

        Args:
            family (str): requested family

        Returns:
            list(float): list of s positions for each element
        """
        elements = self.get_elements(family)
        s_positions = []
        for element in elements:
            s_positions.append(self.get_s(element))
        return s_positions

    def get_devices(self, family, field):
        """Get devices for a specific field for elements in the specfied family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have a device for fields
        'x' and 'y'.

        Args:
            family (str): family of elements
            field (str): field specifying the devices

        Returns:
            list(devices): devices for specified family and field
        """
        elements = self.get_elements(family)
        devices = []
        for element in elements:
            try:
                devices.append(element.get_device(field))
            except KeyError:
                pass

        return devices

    def get_device_names(self, family, field):
        """Get the names for devices attached to a specific field for elements
        in the specfied family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have device for fields
        'x' and 'y'.

        Args:
            family (str): family of elements
            field (str): field specifying the devices

        Returns:
            list(str): devices names for specified family and field
        """
        devices = self.get_devices(family, field)
        return [device.name for device in devices]
