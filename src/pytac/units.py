"""Classes for use in unit conversion."""
from typing import Any, Callable, List, Optional

import numpy
from scipy.interpolate import PchipInterpolator

import pytac
from pytac.exceptions import UnitsException


def unit_function(value: float) -> float:
    """Default value for the pre and post functions used in unit conversion.

    Args:
        value: The value to be converted.

    Returns:
        The result of the conversion.
    """
    return value


class UnitConv:
    """Class to convert between physics and engineering units.

    This class does not do conversion but does return values if the target
    units are the same as the provided units. Subclasses should implement
    _raw_eng_to_phys() and _raw_phys_to_eng() in order to provide complete
    unit conversion.

    The two arguments to this function represent functions that are
    applied to the result of the initial conversion. One happens after
    the conversion, the other happens before the conversion back.
    """

    name: Optional[str]
    """An identifier for the unit conversion object."""
    eng_units: str
    """The unit type of the post conversion engineering value."""
    phys_units: str
    """The unit type of the post conversion physics value."""

    _post_eng_to_phys: Callable[[float], float]
    """Function to be applied after the initial conversion."""
    _pre_phys_to_eng: Callable[[float], float]
    """Function to be applied before the initial conversion."""

    def __init__(
        self,
        post_eng_to_phys: Callable[[float], float] = unit_function,
        pre_phys_to_eng: Callable[[float], float] = unit_function,
        engineering_units: str = "",
        physics_units: str = "",
        name: Optional[str] = None,
    ) -> None:
        """Initialise the UnitConv Object.

        Args:
            post_eng_to_phys: Function to be applied after the initial conversion.
            pre_phys_to_eng: Function to be applied before the initial conversion.
            engineering_units: The unit type of the post conversion engineering value.
            physics_units: The unit type of the post conversion physics value.
            name: An identifier for the unit conversion object.
        """
        self.name = name
        self._post_eng_to_phys = post_eng_to_phys
        self._pre_phys_to_eng = pre_phys_to_eng
        self.eng_units = engineering_units
        self.phys_units = physics_units
        self.lower_limit: Optional[float] = None
        self.upper_limit: Optional[float] = None

    def __str__(self) -> str:
        string_rep = self.__class__.__name__
        if self.name is not None:
            string_rep += f" {self.name}"
        return string_rep

    def set_post_eng_to_phys(self, post_eng_to_phys: Callable[[float], float]) -> None:
        """Set the function to be applied after the initial conversion.

        Args:
            post_eng_to_phys: Function to be applied after the initial conversion.
        """
        self._post_eng_to_phys = post_eng_to_phys

    def set_pre_phys_to_eng(self, pre_phys_to_eng: Callable[[float], float]) -> None:
        """Set the function to be applied before the initial conversion.

        Args:
            pre_phys_to_eng: Function to be applied before the initial conversion.
        """
        self._pre_phys_to_eng = pre_phys_to_eng

    def _raw_eng_to_phys(self, value: float):
        """Function to be implemented by child classes.

        Args:
            value: The engineering value to be converted to physics units.
        """
        raise NotImplementedError(f"{self}: No eng-to-phys conversion provided")

    def eng_to_phys(self, value: float) -> float:
        """Function that does the unit conversion.

        Conversion from engineering to physics units. An additional function
        may be cast on the initial conversion.

        Args:
            value: Value to be converted from engineering to physics units.

        Returns:
            The result value.

        Raises:
            UnitsException: If the conversion is invalid; i.e. if there are no
                solutions, or multiple, within conversion limits.
        """
        if self.lower_limit is not None and value < self.lower_limit:
            raise UnitsException(
                f"{self}: Input less than lower "
                f"conversion limit ({self.lower_limit})."
            )
        if self.upper_limit is not None and value > self.upper_limit:
            raise UnitsException(
                f"{self}: Input greater than upper "
                f"conversion limit ({self.upper_limit})."
            )
        results = self._raw_eng_to_phys(value)
        valid_results = [self._post_eng_to_phys(result) for result in results]
        if len(valid_results) == 0:
            # This will not occur for our existing NullUnitConv,
            # PchipUintConv, and PolyUnitConv classes.
            raise UnitsException(f"{self}: No corresponding physics value exists.")
        elif len(valid_results) > 1:
            # This will not occur for our existing NullUnitConv,
            # PchipUintConv, and PolyUnitConv classes.
            raise UnitsException(
                f"{self}: Multiple corresponding physics values ({valid_results})."
            )
        return valid_results[0]

    def _raw_phys_to_eng(self, value: float):
        """Function to be implemented by child classes.

        Args:
            value: The physics value to be converted to engineering units.
        """
        raise NotImplementedError(f"{self}: No phys-to-eng conversion provided")

    def phys_to_eng(self, value: float) -> float:
        """Function that does the unit conversion.

        Conversion from physics to engineering units. An additional function
        may be cast on the initial conversion.

        Args:
            value: Value to be converted from physics to engineering units.

        Returns:
            The result value.

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
        if len(valid_results) == 0:
            raise UnitsException(
                f"{self}: None of conversion results {results} within "
                f"conversion limits ({self.lower_limit}, {self.upper_limit})."
            )
        elif len(valid_results) > 1:
            raise UnitsException(
                f"{self}: There are multiple "
                f"corresponding engineering values ({valid_results})."
            )
        return valid_results[0]

    def convert(self, value: float, origin: str, target: str) -> float:
        """Convert between two different unit types and check the validity of
        the result.

        Args:
            value: the value to be converted
            origin: pytac.ENG or pytac.PHYS
            target: pytac.ENG or pytac.PHYS

        Returns:
            The resulting value.

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
                f"{self}: Conversion from {origin} to {target} not understood."
            )

    def set_conversion_limits(self, lower_limit: float, upper_limit: float) -> None:
        """Conversion limits to be applied before or after a conversion take
        place. Limits should be set in in engineering units.

        Args:
            lower_limit: the lower conversion limit
            upper_limit: the upper conversion limit
        """
        if (lower_limit is not None) and (upper_limit is not None):
            if lower_limit >= upper_limit:
                raise ValueError(
                    f"Lower conversion limit ({lower_limit}) must be less "
                    f"than the upper limit ({upper_limit})."
                )
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def get_conversion_limits(self, units: str = pytac.ENG) -> List[float]:
        """Return the current conversion limits in the specified unit type.

        Args:
            units: The unit type.

        Returns:
            The conversion limits in the desired unit type,
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
            raise UnitsException(f"{self}: Unit type {units} not understood.")


class PolyUnitConv(UnitConv):
    """Linear interpolation for converting between physics and engineering
    units.
    """

    p: numpy.poly1d
    """A one-dimensional polynomial of coefficients."""

    def __init__(
        self,
        coef: numpy.ndarray[Any, numpy.dtype[numpy.generic]],
        post_eng_to_phys: Callable[[float], float] = unit_function,
        pre_phys_to_eng: Callable[[float], float] = unit_function,
        engineering_units: str = "",
        physics_units: str = "",
        name: Optional[str] = None,
    ):
        """Initialise the PolyUnitConv Object.

        Args:
            coef: The polynomial's coefficients, in decreasing powers.
            post_eng_to_phys: The value after conversion between ENG and PHYS.
            pre_eng_to_phys: The value before conversion.
            engineering_units: The unit type of the post conversion engineering value.
            physics_units: The unit type of the post conversion physics value.
            name: An identifier for the unit conversion object.
        """
        super(self.__class__, self).__init__(
            post_eng_to_phys, pre_phys_to_eng, engineering_units, physics_units, name
        )
        self.p = numpy.poly1d(coef)

    def _raw_eng_to_phys(self, eng_value: float) -> List[float]:
        """Convert between engineering and physics units.

        Args:
            eng_value: The engineering value to be converted to physics units.

        Returns:
            Containing the converted physics value from the given
                engineering value.
        """
        return [self.p(eng_value)]

    def _raw_phys_to_eng(self, physics_value: float) -> List[float]:
        """Convert between physics and engineering units.

        Args:
            physics_value: The physics value to be converted to
                engineering units.

        Returns:
            Containing all posible real engineering values converted
                from the given physics value.
        """
        roots = set((self.p - physics_value).roots)  # remove duplicates
        valid_roots = []
        for root in roots:  # remove imaginary roots
            if not numpy.issubdtype(root.dtype, numpy.complexfloating):
                valid_roots.append(root)
        return valid_roots


class PchipUnitConv(UnitConv):
    """Piecewise Cubic Hermite Interpolating Polynomial unit conversion."""

    x: List[Any]
    """A list of points on the x axis. These must be in increasing order for the
        interpolation to work. Otherwise, a ValueError is raised."""
    y: List[Any]
    """A list of points on the y axis. These must be in increasing or decreasing
        order. Otherwise, a ValueError is raised."""
    pp: PchipInterpolator
    """A pchip one-dimensional monotonic cubic interpolation of points on both x
        and y axes."""

    def __init__(
        self,
        x: List[Any],
        y: List[Any],
        post_eng_to_phys: Callable[[float], float] = unit_function,
        pre_phys_to_eng: Callable[[float], float] = unit_function,
        engineering_units: str = "",
        physics_units: str = "",
        name: Optional[str] = None,
    ) -> None:
        """
        Args:
            x: A list of points on the x axis. These must be in increasing order for
                the interpolation to work. Otherwise, a ValueError is raised.
            y: A list of points on the y axis. These must be in increasing or
                decreasing order. Otherwise, a ValueError is raised.
            engineering_units: The unit type of the post conversion engineering value.
            physics_units: The unit type of the post conversion physics value.
            name: An identifier for the unit conversion object.

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
                "y coefficients must be monotonically increasing or decreasing."
            )

    def _raw_eng_to_phys(self, eng_value: float) -> List[Any]:
        """Convert between engineering and physics units.

        Args:
            eng_value: The engineering value to be converted to physics units.
        Returns:
            Containing the converted physics value from the given engineering value.
        """
        return [self.pp(eng_value)]

    def _raw_phys_to_eng(self, physics_value: float):
        """Convert between physics and engineering units.

        Args:
            physics_value: The physics value to be converted to engineering units.

        Returns:
            Containing all posible real engineering values converted from the given
                physics value.
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
    """Returns input value without performing any conversions."""

    def __init__(self, engineering_units: str = "", physics_units: str = "") -> None:
        """Initialise the NullUnitConv Object.

        Args:
            engineering_units: The unit type of the post conversion engineering value.
            physics_units: The unit type of the post conversion physics value.
        """
        super(self.__class__, self).__init__(
            unit_function, unit_function, engineering_units, physics_units
        )

    def _raw_eng_to_phys(self, eng_value: float) -> List[Any]:
        """Doesn't convert between engineering and physics units.

        Maintains the same syntax as the other UnitConv classes for
        compatibility, but does not perform any conversion.

        Args:
            eng_value: The engineering value to be returned unchanged.

        Returns:
            Containing the unconverted given engineering value.
        """
        return [eng_value]

    def _raw_phys_to_eng(self, phys_value: float) -> List[Any]:
        """Doesn't convert between physics and engineering units.

        Maintains the same syntax as the other UnitConv classes for
        compatibility, but does not perform any conversion.

        Args:
            physics_value: The physics value to be returned unchanged.

        Returns:
            Containing the unconverted given physics value.
        """
        return [phys_value]
