""" Representation of a lattice object which contains all the elements of the machine."""
import numpy


class LatticeException(Exception):
    pass


class Lattice(object):

    def __init__(self, name, control_system, energy):
        """Representation of a lattice.

        Represents a lattice object that contains all elements
        of the ring. It has a name and a control system to be used
        for unit conversion.

        Args:
            name (string): The name of the lattice.
            control_system (ControlSystem): The control system used
                to store the values on a pv.
            energy(Number): The total energy of the lattice.
        """
        self.name = name
        self._lattice = []
        self._cs = control_system
        self._energy = energy
        self._model = None

    def set_model(self, model):
        self._model = model

    def get_energy(self):
        """Function to get the total energy of the lattice.

        Returns:
            Number: The total energy of the lattice.
        """
        return self._energy

    def __getitem__(self, n):
        """Get the nth element of the lattice.

        Args:
            n (int): An index that represents the nth + 1 element of the
                lattice.

        Returns:
            Element: The element asked by the index n.
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
        """Add an element to the lattice.

        Args:
            element (Element): The element to be inserted into the lattice.
        """
        self._lattice.append(element)

    def get_elements(self, family=None, cell=None):
        """Get the elements of a family from the lattice.

        If no family is specified it returns all elements.

        Elements are returned in the order they exist in the ring.

        Args:
            family (string): Restrict elements to those in this family
            cell (int): Restrict elements to those in the specified cell

        Returns:
            list(Element): A list that contains all elements of the specified family.
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
        """Get all available families of the lattice.

        Returns:
            set(string): Contains all available families in the lattice.
        """
        families = set()
        for element in self._lattice:
            for family in element.families:
                families.add(family)

        return families

    def get_pv_names(self, family, field, handle):
        """Get all pv names for a specific family, field and handle.

        Args:
            family (string): A specific family to requests elements of.
            field (string): The field to uniquely identify a device.
            handle (string): It is used to identify a readback or setpoint pv.

        Returns:
            list(string): A list of readback or setpoint pvs from the device.
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

    def get_s(self, element):
        """Find the position of a given element in the lattice.

        Note that the given element must exist in the lattice.

        Args:
            given_element: The element that the position is being asked for.

        Returns:
            float: the position of the given element.

        Raises
            LatticeException: if element doesn't exist in the lattice.
        """
        s_pos = 0
        for el in self._lattice:
            if el is not element:
                s_pos += el.length
            else:
                return s_pos
        raise LatticeException('Element {} does not exist in the lattice'.format(element))

    def get_family_s(self, family):
        """Get the positions for a set of elements from the same family.

        Args:
            family(string): The family the positions are being asked for.

        Returns:
            list(float): A list of floating point numbers that represent the positions
            for each element.
        """
        elements = self.get_elements(family)
        s_positions = []
        for element in elements:
            s_positions.append(self.get_s(element))
        return s_positions

    def get_devices(self, family, field):
        """Get devices attached to a specific field for elements in the specfied family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have device for fields 'x' and 'y'.

        Args:
            family: family of elements
            field: field specifying the devices

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
        """Get the names for devices attached to a specific field for elements in the specfied family.

        Typically all elements of a family will have devices associated with
        the same fields - for example, BPMs each have device for fields 'x' and 'y'.

        Args:
            family: family of elements
            field: field specifying the devices

        Returns:
            list(devices): devices for specified family and field
        """
        devices = self.get_devices(family, field)
        return [device.name for device in devices]
