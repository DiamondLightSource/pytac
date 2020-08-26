"""Classes for use in unit conversion."""
import numpy
from scipy.interpolate import PchipInterpolator

import pytac
from pytac.exceptions import UnitsException


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
        name (str): An identifier for the unit conversion object.
        eng_units (str): The unit type of the post conversion engineering
                          value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Function to be applied after the
                                         initial conversion.
           _pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
    """

    def __init__(
        self,
        post_eng_to_phys=unit_function,
        pre_phys_to_eng=unit_function,
        engineering_units="",
        physics_units="",
        name=None,
    ):
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
            name (str): An identifier for the unit conversion object.

        **Methods:**
        """
        self.name = name
        self._post_eng_to_phys = post_eng_to_phys
        self._pre_phys_to_eng = pre_phys_to_eng
        self.eng_units = engineering_units
        self.phys_units = physics_units
        self.lower_limit = None
        self.upper_limit = None

    def __str__(self):
        string_rep = self.__class__.__name__
        if self.name is not None:
            string_rep += " {}".format(self.name)
        return string_rep

    def set_post_eng_to_phys(self, post_eng_to_phys):
        """Set the function to be applied after the initial conversion.
        Args:
            post_eng_to_phys (function): Function to be applied after the
                                          initial conversion.
        """
        self._post_eng_to_phys = post_eng_to_phys

    def set_pre_phys_to_eng(self, pre_phys_to_eng):
        """Set the function to be applied before the initial conversion.
        Args:
            pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
        """
        self._pre_phys_to_eng = pre_phys_to_eng

    def _raw_eng_to_phys(self, value):
        """Function to be implemented by child classes.

        Args:
            value (float): The engineering value to be converted to physics
                            units.
        """
        raise NotImplementedError(
            "{0}: No eng-to-phys conversion provided".format(self)
        )

    def eng_to_phys(self, value):
        """Function that does the unit conversion.

        Conversion from engineering to physics units. An additional function
        may be cast on the initial conversion.

        Args:
            value (float): Value to be converted from engineering to physics
                            units.

        Returns:
            float: The result value.

        Raises:
            UnitsException: If the conversion is invalid; i.e. if there are no
                            solutions, or multiple, within conversion limits.
        """
        if self.lower_limit is not None:
            if value < self.lower_limit:
                raise UnitsException(
                    "{0}: Input less than lower "
                    "conversion limit ({1}).".format(self, self.lower_limit)
                )
        if self.upper_limit is not None:
            if value > self.upper_limit:
                raise UnitsException(
                    "{0}: Input greater than "
                    "upper conversion limit ({1}).".format(self, self.upper_limit)
                )
        results = self._raw_eng_to_phys(value)
        valid_results = [self._post_eng_to_phys(result) for result in results]
        if len(valid_results) == 1:
            result = valid_results[0]
        elif len(valid_results) == 0:
            # This will not occur for our existing NullUnitConv,
            # PchipUintConv, and PolyUnitConv classes.
            raise UnitsException(
                "{0}: A corresponding physics value " "does not exist.".format(self)
            )
        else:
            # This will not occur for our existing NullUnitConv,
            # PchipUintConv, and PolyUnitConv classes.
            raise UnitsException(
                "{0}: There are multiple "
                "corresponding physics values ({1}).".format(self, valid_results)
            )
        return result

    def _raw_phys_to_eng(self, value):
        """Function to be implemented by child classes.

        Args:
            value (float): The physics value to be converted to engineering
                            units.
        """
        raise NotImplementedError(
            "{0}: No phys-to-eng conversion provided".format(self)
        )

    def phys_to_eng(self, value):
        """Function that does the unit conversion.

        Conversion from physics to engineering units. An additional function
        may be cast on the initial conversion.

        Args:
            value (float): Value to be converted from physics to engineering
                            units.

        Returns:
            float: The result value.

        Raises:
            UnitsException: If the conversion is invalid; i.e. if there are no
                            solutions, or multiple, within conversion limits.
        """
        adjusted_value = self._pre_phys_to_eng(value)
        results = self._raw_phys_to_eng(adjusted_value)

        valid_results = results[:]

        if self.lower_limit is not None:
            valid_results = [r for r in valid_results if r >= self.lower_limit]
        if self.upper_limit is not None:
            valid_results = [r for r in valid_results if r <= self.upper_limit]
        if len(valid_results) == 1:
            return valid_results[0]
        elif len(valid_results) == 0:
            raise UnitsException(
                "{0}: none of conversion results {1} "
                "within conversion limits ({2}, "
                "{3}).".format(self, results, self.lower_limit, self.upper_limit)
            )
        else:
            raise UnitsException(
                "{0}: There are multiple "
                "corresponding engineering values ({1}).".format(self, valid_results)
            )

    def convert(self, value, origin, target):
        """Convert between two different unit types and chek the validity of
        the result.

        Args:
            value (float): the value to be converted
            origin (str): pytac.ENG or pytac.PHYS
            target (str): pytac.ENG or pytac.PHYS

        Returns:
            float: The resulting value.

        Raises:
            UnitsException: If the conversion is invalid; i.e. if there are no
                             solutions, or multiple, within conversion limits.
        """
        if origin == target:
            return value
        elif origin == pytac.ENG and target == pytac.PHYS:
            return self.eng_to_phys(value)
        elif origin == pytac.PHYS and target == pytac.ENG:
            return self.phys_to_eng(value)
        else:
            raise UnitsException(
                "{0}: Conversion from {1} to {2} "
                "not understood.".format(self, origin, target)
            )

    def set_conversion_limits(self, lower_limit, upper_limit):
        """Conversion limits to be applied before or after a conversion take
        place. Limits should be set in in engineering units.

        Args:
            lower_limit (float): the lower conversion limit
            upper_limit (float): the upper conversion limit
        """
        if (lower_limit is not None) and (upper_limit is not None):
            if lower_limit >= upper_limit:
                raise ValueError(
                    "Lower conversion limit ({0}) must be less "
                    "than the upper limit ({1}).".format(lower_limit, upper_limit)
                )
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def get_conversion_limits(self, units=pytac.ENG):
        """Return the current conversion limits in the specified unit type.

        Args:
            units:

        Returns:
            list: the conversion limits in the desired unit type,
                   format: [lower_limit, upper_limit]
        """
        if units == pytac.ENG:
            return [self.lower_limit, self.upper_limit]
        elif units == pytac.PHYS:
            return [
                self.convert(self.lower_limit, pytac.ENG, pytac.PHYS),
                self.convert(self.upper_limit, pytac.ENG, pytac.PHYS),
            ]
        else:
            raise UnitsException(
                "{0}: Unit type {1} not understood.".format(self, units)
            )


class PolyUnitConv(UnitConv):
    """Linear interpolation for converting between physics and engineering
    units.

    **Attributes:**

    Attributes:
        p (poly1d): A one-dimensional polynomial of coefficients.
        name (str): An identifier for the unit conversion object.
        eng_units (str): The unit type of the post conversion engineering
                          value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Function to be applied after the
                                         initial conversion.
           _pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
    """

    def __init__(
        self,
        coef,
        post_eng_to_phys=unit_function,
        pre_phys_to_eng=unit_function,
        engineering_units="",
        physics_units="",
        name=None,
    ):
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
            name (str): An identifier for the unit conversion object.
        """
        super(self.__class__, self).__init__(
            post_eng_to_phys, pre_phys_to_eng, engineering_units, physics_units, name
        )
        self.p = numpy.poly1d(coef)

    def _raw_eng_to_phys(self, eng_value):
        """Convert between engineering and physics units.

        Args:
            eng_value (float): The engineering value to be converted to physics
                                units.

        Returns:
            list: Containing the converted physics value from the given
                    engineering value.
        """
        return [self.p(eng_value)]

    def _raw_phys_to_eng(self, physics_value):
        """Convert between physics and engineering units.

        Args:
            physics_value (float): The physics value to be converted to
                                    engineering units.

        Returns:
            list: Containing all posible real engineering values converted
                   from the given physics value.
        """
        roots = set((self.p - physics_value).roots)  # remove duplicates
        valid_roots = []
        for root in roots:  # remove imaginary roots
            if not numpy.issubdtype(root.dtype, numpy.complexfloating):
                valid_roots.append(root)
        return valid_roots


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

        name (str): An identifier for the unit conversion object.
        eng_units (str): The unit type of the post conversion engineering
                          value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Function to be applied after the
                                         initial conversion.
           _pre_phys_to_eng (function): Function to be applied before the
                                         initial conversion.
    """

    def __init__(
        self,
        x,
        y,
        post_eng_to_phys=unit_function,
        pre_phys_to_eng=unit_function,
        engineering_units="",
        physics_units="",
        name=None,
    ):
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
            name (str): An identifier for the unit conversion object.

        Raises:
            ValueError: if coefficients are not appropriately monotonic.
        """
        super(self.__class__, self).__init__(
            post_eng_to_phys, pre_phys_to_eng, engineering_units, physics_units, name
        )
        self.x = x
        self.y = y
        self.pp = PchipInterpolator(x, y)
        # Set conversion limits to PChip bounds if they are not already set.
        if self.lower_limit is None:
            self.lower_limit = self.x[0]
        if self.upper_limit is None:
            self.upper_limit = self.x[-1]
        # Note that the x coefficients are checked by the PchipInterpolator
        # constructor.
        y_diff = numpy.diff(y)
        if not ((numpy.all(y_diff > 0)) or (numpy.all((y_diff < 0)))):
            raise ValueError(
                "y coefficients must be monotonically " "increasing or decreasing."
            )

    def _raw_eng_to_phys(self, eng_value):
        """Convert between engineering and physics units.

        Args:
            eng_value (float): The engineering value to be converted to physics
                                units.
        Returns:
            list: Containing the converted physics value from the given
                    engineering value.
        """
        return [self.pp(eng_value)]

    def _raw_phys_to_eng(self, physics_value):
        """Convert between physics and engineering units.

        Args:
            physics_value (float): The physics value to be converted to
                                    engineering units.

        Returns:
            list: Containing all posible real engineering values converted
                   from the given physics value.
        """
        y = [val - physics_value for val in self.y]
        new_pp = PchipInterpolator(self.x, y)
        roots = set(new_pp.roots())  # remove duplicates
        valid_roots = []
        for root in roots:  # remove imaginary roots
            if not numpy.issubdtype(root.dtype, numpy.complexfloating):
                valid_roots.append(root)
        return valid_roots


class NullUnitConv(UnitConv):
    """Returns input value without performing any conversions.

    **Attributes:**

    Attributes:
        eng_units (str): The unit type of the post conversion engineering
                          value.
        phys_units (str): The unit type of the post conversion physics value.

    .. Private Attributes:
           _post_eng_to_phys (function): Always unit_function as no conversion
                                          is performed.
           _pre_phys_to_eng (function): Always unit_function as no conversion
                                          is performed.
    """

    def __init__(self, engineering_units="", physics_units=""):
        """
        Args:
            engineering_units (str): The unit type of the post conversion
                                      engineering value.
            physics_units (str): The unit type of the post conversion physics
                                  value.
        """
        super(self.__class__, self).__init__(
            unit_function, unit_function, engineering_units, physics_units
        )

    def _raw_eng_to_phys(self, eng_value):
        """Doesn't convert between engineering and physics units.

        Maintains the same syntax as the other UnitConv classes for
        compatibility, but does not perform any conversion.

        Args:
            eng_value (float): The engineering value to be returned unchanged.
        Returns:
            list: Containing the unconverted given engineering value.
        """
        return [eng_value]

    def _raw_phys_to_eng(self, phys_value):
        """Doesn't convert between physics and engineering units.

        Maintains the same syntax as the other UnitConv classes for
        compatibility, but does not perform any conversion.

        Args:
            physics_value (float): The physics value to be returned unchanged.

        Returns:
            list: Containing the unconverted given physics value.
        """
        return [phys_value]
