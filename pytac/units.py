"""Classes for use in unit conversion."""
import pytac
import numpy
from pytac.exceptions import UnitsException
from scipy.interpolate import PchipInterpolator


def unit_function(value):
    """Default value for the pre and post functions used in unit conversion.

    Args:
        value (float): The value to be converted.

    Returns:
        float: The result of the conversion.
    """
    return value


class UnitConv(object):
    """Class to convert between physics and engineering units.

    This class does not do conversion but does return values if the target
    units are the same as the provided units. Subclasses should implement
    _raw_eng_to_phys() and _raw_phys_to_eng() in order to provide complete
    unit conversion.

    The two arguments to this function represent functions that are
    applied to the result of the initial conversion. One happens after
    the conversion, the other happens before the conversion back.

    **Attributes:**

    Attributes:
        eng_units (str): The unit type of the post conversion engineering value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Function to be applied after the
                                         initial conversion.
           _pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
    """

    def __init__(self, post_eng_to_phys=unit_function,
                 pre_phys_to_eng=unit_function, engineering_units=None,
                 physics_units=None):
        """
        Args:
            post_eng_to_phys (function): Function to be applied after the
                                          initial conversion.
            pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
            engineering_units (str): The unit type of the post conversion
                                      engineering value.
            physics_units (str): The unit type of the post conversion physics
                                  value.

        **Methods:**
        """
        self._post_eng_to_phys = post_eng_to_phys
        self._pre_phys_to_eng = pre_phys_to_eng
        self.eng_units = engineering_units
        self.phys_units = physics_units

    def _raw_eng_to_phys(self, value):
        """Function to be implemented by child classes.

        Args:
            value (float): The engineering value to be converted to physics
                            units.
        """
        raise NotImplementedError('No eng-to-phys conversion provided')

    def eng_to_phys(self, value):
        """Function that does the unit conversion.

        Conversion from engineering to physics units. An additional function
        may be cast on the initial conversion.

        Args:
            value (float): Value to be converted from engineering to physics
                            units.

        Returns:
            float: The result value.
        """
        x = self._raw_eng_to_phys(value)
        result = self._post_eng_to_phys(x)
        return result

    def _raw_phys_to_eng(self, value):
        """Function to be implemented by child classes.

        Args:
            value (float): The physics value to be converted to engineering
                            units.
        """
        raise NotImplementedError('No phys-to-eng conversion provided')

    def phys_to_eng(self, value):
        """Function that does the unit conversion.

        Conversion from physics to engineering units. An additional function
        may be cast on the initial conversion.

        Args:
            value (float): Value to be converted from physics to engineering
                            units.

        Returns:
            float: The result value.
        """
        x = self._pre_phys_to_eng(value)
        result = self._raw_phys_to_eng(x)
        return result

    def convert(self, value, origin, target):
        """
        Args:
            value (float):
            origin (str): pytac.ENG or pytac.PHYS
            target (str): pytac.ENG or pytac.PHYS

        Returns:
            float: The result value.

        Raises:
            UnitsException: invalid conversion.
        """
        if origin == target:
            return value
        if origin == pytac.PHYS and target == pytac.ENG:
            return self.phys_to_eng(value)
        if origin == pytac.ENG and target == pytac.PHYS:
            return self.eng_to_phys(value)
        raise UnitsException(
            'Conversion {} to {} not understood'.format(origin, target))


class PolyUnitConv(UnitConv):
    """Linear interpolation for converting between physics and engineering
    units.

    **Attributes:**

    Attributes:
        p (poly1d): A one-dimensional polynomial of coefficients.
        eng_units (str): The unit type of the post conversion engineering value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Function to be applied after the
                                         initial conversion.
           _pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
    """
    def __init__(self, coef, post_eng_to_phys=unit_function,
                 pre_phys_to_eng=unit_function, engineering_units=None,
                 physics_units=None):
        """
        Args:
            coef (array-like): The polynomial's coefficients, in decreasing
                                powers.
            post_eng_to_phys (float): The value after conversion between ENG
                                       and PHYS.
            pre_eng_to_phys (float): The value before conversion.
            engineering_units (str): The unit type of the post conversion
                                      engineering value.
            physics_units (str): The unit type of the post conversion physics
                                  value.
        """
        super(self.__class__, self).__init__(post_eng_to_phys, pre_phys_to_eng,
                                             engineering_units, physics_units)
        self.p = numpy.poly1d(coef)

    def _raw_eng_to_phys(self, eng_value):
        """Convert between engineering and physics units.

        Args:
            eng_value (float): The engineering value to be converted to physics
                                units.

        Returns:
            float: The converted physics value from the given engineering value.
        """
        return self.p(eng_value)

    def _raw_phys_to_eng(self, physics_value):
        """Convert between physics and engineering units.

        Args:
            physics_value (float): The physics value to be converted to
                                    engineering units.

        Returns:
            float: The converted engineering value from the given physics value.

        Raises:
            ValueError: An error occurred when there exist no or more than one
                         roots.
        """
        roots = (self.p - physics_value).roots
        if len(roots) == 1:
            x = roots[0]
            return x
        else:
            raise ValueError("There doesn't exist a corresponding engineering "
                             "value or they are not unique:", roots)


class PchipUnitConv(UnitConv):
    """Piecewise Cubic Hermite Interpolating Polynomial unit conversion.

    **Attributes:**

    Attributes:
        x (list): A list of points on the x axis. These must be in increasing
                   order for the interpolation to work. Otherwise, a ValueError
                   is raised.
        y (list): A list of points on the y axis. These must be in increasing
                   or decreasing order. Otherwise, a ValueError is raised.
        pp (PchipInterpolator): A pchip one-dimensional monotonic cubic
                                 interpolation of points on both x and y axes.
        eng_units (str): The unit type of the post conversion engineering value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Function to be applied after the
                                         initial conversion.
           _pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
    """
    def __init__(self, x, y, post_eng_to_phys=unit_function,
                 pre_phys_to_eng=unit_function, engineering_units=None,
                 physics_units=None):
        """
        Args:
            x (list): A list of points on the x axis. These must be in
                       increasing order for the interpolation to work.
                       Otherwise, a ValueError is raised.
            y (list): A list of points on the y axis. These must be in
                       increasing or decreasing order. Otherwise, a ValueError
                       is raised.
            engineering_units (str): The unit type of the post conversion
                                      engineering value.
            physics_units (str): The unit type of the post conversion physics
                                  value.

        Raises:
            ValueError: if coefficients are not appropriately monotonic.
        """
        super(self.__class__, self).__init__(post_eng_to_phys, pre_phys_to_eng,
                                             engineering_units, physics_units)
        self.x = x
        self.y = y
        self.pp = PchipInterpolator(x, y)
        # Note that the x coefficients are checked by the PchipInterpolator
        # constructor.
        y_diff = numpy.diff(y)
        if not ((numpy.all(y_diff > 0)) or (numpy.all((y_diff < 0)))):
            raise ValueError("y coefficients must be monotonically"
                             "increasing or decreasing.")

    def _raw_eng_to_phys(self, eng_value):
        """Convert between engineering and physics units.

        Args:
            eng_value (float): The engineering value to be converted to physics
                                units.
        Returns:
            float: The converted physics value from the given engineering value.
        """
        return self.pp(eng_value)

    def _raw_phys_to_eng(self, physics_value):
        """Convert between physics and engineering units.

        This expects there to be exactly one solution for x within the
        range of the x values in self.x, otherwise a UnitsException is raised.

        Args:
            physics_value (float): The physics value to be converted to
                                    engineering units.

        Returns:
            float: The converted engineering value from the given physics
                    value.

        Raises:
            UnitsException: if there is not exactly one solution.
        """
        y = [val - physics_value for val in self.y]
        new_pp = PchipInterpolator(self.x, y)
        roots = new_pp.roots()

        unique_root = None
        for root in roots:
            if self.x[0] <= root <= self.x[-1]:
                if unique_root is None:
                    unique_root = root
                else:
                    # I believe this should not happen because of the
                    # requirement for self.y to be monotonically increasing.
                    raise UnitsException(
                        "More than one solution within Pchip bounds"
                    )
        if unique_root is None:
            raise UnitsException("No solution within Pchip bounds.")
        return unique_root


class NullUnitConv(UnitConv):
    """Returns input value without performing any conversions.

    **Attributes:**

    Attributes:
        eng_units (str): The unit type of the post conversion engineering value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Always unit_function as no conversion
                                          is performed.
           _pre_phys_to_eng (function): Always unit_function as no conversion
                                          is performed.
    """
    def __init__(self, engineering_units=None, physics_units=None):
        """
        Args:
            engineering_units (str): The unit type of the post conversion
                                      engineering value.
            physics_units (str): The unit type of the post conversion physics
                                  value.
        """
        super(self.__class__, self).__init__(unit_function, unit_function,
                                             engineering_units, physics_units)

    def _raw_eng_to_phys(self, eng_value):
        """Doesn't convert between engineering and physics units.

        Maintains the same syntax as the other UnitConv classes for
        compatibility, but does not perform any conversion.

        Args:
            eng_value (float): The engineering value to be returned unchanged.
        Returns:
            float: The unconverted given engineering value.
        """
        return eng_value

    def _raw_phys_to_eng(self, phys_value):
        """Doesn't convert between physics and engineering units.

        Maintains the same syntax as the other UnitConv classes for
        compatibility, but does not perform any conversion.

        Args:
            physics_value (float): The physics value to be returned unchanged.

        Returns:
            float: The unconverted given physics value.
        """
        return phys_value
