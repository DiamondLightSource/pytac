"""EPICS implementations of the classes in pytac."""
import numpy
import pytac
from pytac.device import Device
from pytac.element import Element
from pytac.exceptions import DeviceException, HandleException, LatticeException
from pytac.lattice import Lattice


class EpicsLattice(Lattice):
    """EPICS-aware lattice class.

    Allows efficient get_values() and set_values() methods, and adds
    get_pv_names() method.

    """

    def __init__(self, name, epics_cs):
        """
        Args:
            name (str): The name of the epics lattice.
            epics_cs (ControlSystem): The control system used to store the
                                       values on a PV.

        **Methods:**
        """
        super(EpicsLattice, self).__init__(name)
        self._cs = epics_cs

    def get_pv_names(self, field, handle):
        """Get the PV name for a specific field, and handle.

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
            raise DeviceException('{} has no device for field {}'
                                  .format(self, field))

    def get_element_pv_names(self, family, field, handle):
        """Get all PV names for a specific family, field, and handle.

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

    def get_element_values(self, family, field, handle, dtype=None):
        """Get the value for a family and field for all elements in the lattice.

        Args:
            family (str): requested family.
            field (str): requested field.
            handle (str): pytac.RB or pytac.SP.
            dtype (numpy.dtype): if set it specifies the data type of the values
                                  in the output array.

        Returns:
            list or array: The requested values.
        """
        pv_names = self.get_element_pv_names(family, field, handle)
        values = self._cs.get_multiple(pv_names)
        if dtype is not None:
            values = numpy.array(values, dtype=dtype)
        return values

    def set_element_values(self, family, field, values):
        """Set the value for a family and field for all elements in the lattice.

        Args:
            family (str): requested family.
            field (str): requested field.
            values (sequence): values to be set.
        """
        pv_names = self.get_element_pv_names(family, field, 'setpoint')
        self._cs.set_multiple(pv_names, values)


class EpicsElement(Element):
    """EPICS-aware element.

    Adds get_pv_name() method.

    **Methods:**
    """
    def get_pv_name(self, field, handle):
        """Get PV name for the specified field and handle.

        Args:
            field (str): The requested field.
            handle (str): pytac.RB or pytac.SP.

        Returns:
            str: The readback or setpoint PV for the specified field.

        Raises:
            DeviceException: if there is no device for this field.
        """
        try:
            return (self._data_source_manager._data_sources[pytac.LIVE]
                    .get_device(field).get_pv_name(handle))
        except KeyError:
            raise DeviceException('{} has no device for field {}'
                                  .format(self, field))


class EpicsDevice(Device):
    """An EPICS-aware device.

    Contains a control system, readback and setpoint PVs. A readback
    or setpoint PV is required when creating a device otherwise a
    DeviceException is raised. The device is enabled by default.

    **Attributes:**

    Attributes:
        name (str): The prefix of EPICS PVs for this device.
        rb_pv (str): The EPICS readback PV.
        sp_pv (str): The EPICS setpoint PV.

    .. Private Attributes:
           _cs (ControlSystem): The control system object used to get and set
                                 the value of a PV.
           _enabled (bool-like): Whether the device is enabled. May be a
                                  PvEnabler object.
    """
    def __init__(self, name, cs, enabled=True, rb_pv=None, sp_pv=None):
        """
        Args:
            name (str): The prefix of EPICS PV for this device.
            cs (ControlSystem): The control system object used to get and set
                                 the value of a PV.
            enabled (bool-like): Whether the device is enabled. May be a
                                  PvEnabler object.
            rb_pv (str): The EPICS readback PV.
            sp_pv (str): The EPICS setpoint PV.

        **Methods:**
        """
        self.name = name
        self._cs = cs
        self.rb_pv = rb_pv
        self.sp_pv = sp_pv
        self._enabled = enabled

    def is_enabled(self):
        """Whether the device is enabled.

        Returns:
            bool: whether the device is enabled.
        """
        return bool(self._enabled)

    def set_value(self, value):
        """Set the device value.

        Args:
            value (float): The value to set.

        Raises:
            HandleException: if no setpoint PV exists.
        """
        if self.sp_pv is None:
            raise HandleException("Device {0} has no setpoint PV."
                                  .format(self.name))
        self._cs.set_single(self.sp_pv, value)

    def get_value(self, handle):
        """Read the value of a readback or setpoint PV.

        Args:
            handle (str): pytac.SP or pytac.RB.

        Returns:
            float: The value of the PV.

        Raises:
            HandleException: if the requested PV doesn't exist.
        """
        if handle == pytac.RB and self.rb_pv:
            return self._cs.get_single(self.rb_pv)
        elif handle == pytac.SP and self.sp_pv:
            return self._cs.get_single(self.sp_pv)

        raise HandleException("Device {0} has no {1} PV."
                              .format(self.name, handle))

    def get_pv_name(self, handle):
        """Get the PV name for the specified handle.

        Args:
            handle (str): The readback or setpoint handle to be returned.

        Returns:
            str: A readback or setpoint PV.

        Raises:
            HandleException: if the PV doesn't exist.
        """
        if handle == pytac.RB and self.rb_pv:
            return self.rb_pv
        elif handle == pytac.SP and self.sp_pv:
            return self.sp_pv

        raise HandleException("Device {0} has no {1} PV."
                              .format(self.name, handle))


class PvEnabler(object):
    """A PvEnabler class to check whether a device is enabled.

    The class will behave like True if the PV value equals enabled_value,
    and False otherwise.

    .. Private Attributes:
           _pv (str): The PV name.
           _enabled_value (str): The value for PV for which the device should
                                  be considered enabled.
           _cs (ControlSystem): The control system object.
    """
    def __init__(self, pv, enabled_value, cs):
        """
        Args:
            pv (str): The PV name.
            enabled_value (str): The value for PV for which the device should
                                  be considered enabled.
            cs (ControlSystem): The control system object.

        **Methods:**
        """
        self._pv = pv
        self._enabled_value = str(int(float(enabled_value)))
        self._cs = cs

    def __nonzero__(self):
        """Used to override the 'if object' clause.

        Support for Python 2.7.

        Returns:
            bool: True if the device should be considered enabled.
        """
        pv_value = self._cs.get_single(self._pv)
        return self._enabled_value == str(int(float(pv_value)))

    def __bool__(self):
        """Used to override the 'if object' clause.

        Support for Python 3.x.

        Returns:
            bool: True if the device should be considered enabled.
        """
        return self.__nonzero__()
