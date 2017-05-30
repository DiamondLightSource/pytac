import numpy
from scipy.interpolate import PchipInterpolator
from pytac.exceptions import UniqueSolutionException


def unit_function(value):
    """Default value for the pre and post functions used in unit conversion.

    Args:
        value(Number): The value to be converted.

    Returns:
        value(Number): The result of the conversion.
    """
    return value


class UnitConv(object):
    def __init__(self, post_eng_to_phys=unit_function, pre_phys_to_eng=unit_function):
        """Class to convert between physics and engineering units.

        The two arguments to this function represent functions that are
        applied to the result of the initial conversion. One happens after
        the conversion, the other happens before the conversion back.

        Args:
            post_eng_to_phys(function): Function to be applied post the initial
                conversion.
            pre_phys_to_eng(function): Function to be applied preceding the initial
                conversion.
        """
        self._post_eng_to_phys = post_eng_to_phys
        self._pre_phys_to_eng = pre_phys_to_eng

    def _raw_eng_to_phys(self, value):
        """Function to be implemented by child classes.

        Args:
            value(Number): Value to be converted from engineering to physics untits.
        """
        raise NotImplementedError()

    def eng_to_phys(self, value):
        """Function that does the unit conversion.

        Conversion from engineering to physics units. An additional function may
        be casted on the initial conversion.

        Args:
            value(Number): Value to be converted from engineering to physics units.

        Returns:
            result(Number): The result value.
        """
        x = self._raw_eng_to_phys(value)
        result = self._post_eng_to_phys(x)
        return result

    def _raw_phys_to_eng(self, value):
        """Function to be implemented by child classes.

        Args:
            value(Number): Value to be converted from physics to engineering units.
        """
        raise NotImplementedError()

    def phys_to_eng(self, value):
        """Function that does the unit conversion.

        Conversion from physics to engineering units. An additional function may
        be casted on the initial conversion.

        Args:
            value(Number): Value to be converted from physics to engineering units.

        Returns:
            result(Number): The result value.
        """
        x = self._pre_phys_to_eng(value)
        result = self._raw_phys_to_eng(x)
        return result


class PolyUnitConv(UnitConv):
    def __init__(self, coef, post_eng_to_phys=unit_function, pre_phys_to_eng=unit_function):
        """Linear interpolation for converting between physics and engineering units.

        Args:
            coef(array_like): The polynomial's coefficients, in decreasing powers.
        """
        super(self.__class__, self).__init__(post_eng_to_phys, pre_phys_to_eng)
        self.p = numpy.poly1d(coef)

    def _raw_eng_to_phys(self, eng_value):
        """Convert between engineering and physics units.

        Args:
            eng_value(float): The engineering value to be converted to the engineering unit.

        Returns:
            float: The physics value determined using the engineering value.
        """
        return self.p(eng_value)

    def _raw_phys_to_eng(self, physics_value):
        """Convert between physics and engineering units.

        Args:
            physics_value(float): The physics value to be converted to the
                engineering value.

        Returns:
            float: The converted engineering value from the given physics value.

        Raises:
            ValueError: An error occured when there exist no or more than one roots.
        """
        roots = (self.p - physics_value).roots
        if len(roots) == 1:
            x = roots[0]
            return x
        else:
            raise ValueError("There doesn't exist a corresponding engineering value or "
                             "they are not unique:", roots)


class PchipUnitConv(UnitConv):
    def __init__(self, x, y, post_eng_to_phys=unit_function, pre_phys_to_eng=unit_function):
        """ PChip interpolation for converting between physics and engineering units.

        Args:
            x(list): A list of points on the x axis. These must be in increasing order
                for the interpolation to work. Otherwise, a ValueError is raised.
            y(list): A list of points on the y axis. These must be in increasing or
                decreasing order. Otherwise, a ValueError is raised.

        Raises:
            ValueError: An error occured when the given y coefficients are neither in
            increasing or decreasing order.
        """
        super(self.__class__, self).__init__(post_eng_to_phys, pre_phys_to_eng)
        self.x = x
        self.y = y
        self.pp = PchipInterpolator(x, y)

        diff = numpy.diff(y)
        if not ((numpy.all(diff > 0)) or (numpy.all((diff < 0)))):
            raise ValueError("Given coefficients must be monotonically"
                             "decreasing.")

    def _raw_eng_to_phys(self, eng_value):
        """Convert between engineering and physics units.

        Args:
            eng_value(float): The engineering value to be converted to the engineering unit.
        Returns:
            float: The converted engineering value from the given engineering value.
        """
        return self.pp(eng_value)

    def _raw_phys_to_eng(self, physics_value):
        """Convert between physics and engineering units.

        Args:
            physics_value(float): The engineering value to be converted to the
                engineering value.

        Returns:
            float: The converted engineering value from the given physics value.

        Raises:
            ValueError: An error occured when there exist no or more than one roots.
        """
        y = [val - physics_value for val in self.y]
        new_pp = PchipInterpolator(self.x, y)
        roots = new_pp.roots()

        solution_within_bounds = False
        for root in roots:
            if root <= self.x[-1] and root >= self.x[0]:
                if not solution_within_bounds:
                    solution_within_bounds = True
                    correct_root = root
                else:
                    raise UniqueSolutionException("The function is not invertible.")
        if solution_within_bounds:
            return correct_root
        else:
            raise UniqueSolutionException("The function does not have a solution within the bounds.")
