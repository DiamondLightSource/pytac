from pytac.exceptions import PvException
from pytac.exceptions import ElementNotFoundException

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
            total_length += e.get_length()
        return total_length

    def add_element(self, element):
        """Add an element to the lattice.

        Args:
            element (Element): The element to be inserted into the lattice.
        """
        self._lattice.append(element)

    def get_elements(self, family=None):
        """Get the elements of a family from the lattice.

        If no family is specified it returns the whole lattice.

        Args:
            family (string): A specific family to return the elements of.

        Returns:
            list(Element): A list that contains all elements of the specified family.
        """
        if family is None:
            return self._lattice

        matched_lattice = list()
        for element in self._lattice:
            if family in element.families:
                matched_lattice.append(element)
        return matched_lattice

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

    def get_family_pvs(self, family, field, handle):
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

    def get_family_values(self, family, field, handle='setpoint'):
        """Get all pv values for a set of pvs.

        Args:
            family(string): A specific family to requests the values of.
            field(string): The field to uniquely identify a device.
            handle(string): It is used to identify a readback or setpoint pv.

        Returns:
            list(float): A list of readback or setpoint pv values from the device.
        """
        pv_names = self.get_family_pvs(family, field, handle)
        return self._cs.get(pv_names)

    def set_family_values(self, family, field, values):
        """Set the pv value of a given family of pvs.

        The pvs are determined by family and device. Note that only setpoint
        pvs ca be modified.

        Args:
            family(string): A specific family to set the value of.
            field(string): The field to uniquely identify a device.
            values(list(float)): A list of values to assign to the pvs.

        Raises:
            PvException: An exception raised in case the given list of values
            doesn't match the number of found pvs.

        """
        # Get the number of elements in the family
        pv_names = self.get_family_pvs(family, field, 'setpoint')
        if len(pv_names) != len(values):
            raise PvException("Number of elements in given array must be equal"
                              "to the number of elements in the lattice")
        self._cs.put(pv_names, values)

    def get_s(self, given_element):
        """Find the position of a given element in the lattice.

        Note that the given element must exist in the lattice.

        Args:
            given_element: The element that the position is being asked for.

        Returns:
            float: the position of the given element.

        Raises
            ElementNotFoundException: An exception is raised in case the element
            doesn't exist inside the lattice.
        """
        s_pos = 0
        for element in self._lattice:
            if element is not given_element:
                s_pos += element.get_length()
            else:
                return s_pos
        raise ElementNotFoundException('Given element does not exist in the lattice')

    def get_family_s(self, family):
        """Get the positions for a set of elements from the same family.

        Args:
            family(string): The family the positions are being asked for.

        Returns:
            list(float): A list of floating point numbers that represent the positions
            for each element.
        """
        elements = self.get_elements(family)
        s_positions = list()
        for element in elements:
            s_positions.append(self.get_s(element))
        return s_positions
