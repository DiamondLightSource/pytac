from unittest import mock

import numpy
import pytest

from constants import DUMMY_VALUE_1, DUMMY_VALUE_2, DUMMY_VALUE_3
import pytac
from pytac.units import NullUnitConv, PchipUnitConv, PolyUnitConv, UnitConv


def f1(value):
    return value * 2


def f2(value):
    return value / 2


def test_UnitConv_not_implemented():
    uc = UnitConv(0)
    with pytest.raises(NotImplementedError):
        uc.convert(10, pytac.PHYS, pytac.ENG)
    with pytest.raises(NotImplementedError):
        uc.convert(-11, pytac.ENG, pytac.PHYS)


def test_set_conversion_limits():
    uc = UnitConv(0)
    assert uc.lower_limit is None
    assert uc.upper_limit is None
    uc.set_conversion_limits(0, 1)
    assert uc.lower_limit == 0
    assert uc.upper_limit == 1
    uc.set_conversion_limits(0.1, 2.1)
    assert uc.lower_limit == 0.1
    assert uc.upper_limit == 2.1
    uc.set_conversion_limits(-1, 1e5)
    assert uc.lower_limit == -1
    assert uc.upper_limit == 1e5
    uc.set_conversion_limits(None, 2)
    assert uc.lower_limit is None
    assert uc.upper_limit == 2
    uc.set_conversion_limits(1, None)
    assert uc.lower_limit == 1
    assert uc.upper_limit is None
    uc.set_conversion_limits(None, None)
    assert uc.lower_limit is None
    assert uc.upper_limit is None
    with pytest.raises(ValueError):
        uc.set_conversion_limits(2, 1)


def test_get_conversion_limits():
    uc = PolyUnitConv([2, 0])
    assert uc.get_conversion_limits() == [None, None]
    uc.set_conversion_limits(8, 13)
    assert uc.get_conversion_limits() == [8, 13]
    assert uc.get_conversion_limits(pytac.ENG) == [8, 13]
    assert uc.get_conversion_limits(pytac.PHYS) == [16, 26]
    with pytest.raises(pytac.exceptions.UnitsException):
        uc.get_conversion_limits("invalid-unit-type")


@pytest.mark.parametrize(
    "origin, target", [(pytac.ENG, pytac.PHYS), (pytac.PHYS, pytac.ENG)]
)
def test_UnitConv_raises_UnitsException_for_values_outside_limits(origin, target):
    uc = NullUnitConv()
    uc.set_conversion_limits(0, 10)
    with pytest.raises(pytac.exceptions.UnitsException):
        uc.convert(-1, origin, target)  # below lower limit
    with pytest.raises(pytac.exceptions.UnitsException):
        uc.convert(11, origin, target)  # above upper limit


def test_UnitConv_includes_name_in_exception():
    uc = UnitConv(name="test_unitconv")
    with pytest.raises(NotImplementedError, match="test_unitconv"):
        uc.convert(10, pytac.ENG, pytac.PHYS)


@pytest.mark.parametrize(
    "origin, target", [(pytac.LIVE, pytac.ENG), (pytac.PHYS, pytac.SP), ("a", "b")]
)
def test_UnitConv_requires_correct_arguments(origin, target):
    uc = UnitConv(name=12)
    assert uc.name == 12
    with pytest.raises(pytac.exceptions.UnitsException):
        uc.convert(10, origin, target)


def test_set_post_eng_to_phys():
    uc = UnitConv()
    assert uc._post_eng_to_phys == pytac.units.unit_function
    assert uc._pre_phys_to_eng == pytac.units.unit_function
    m = mock.Mock()
    uc.set_post_eng_to_phys(m)
    assert uc._post_eng_to_phys == m
    assert uc._pre_phys_to_eng == pytac.units.unit_function


def test_set_per_phys_to_eng():
    uc = UnitConv()
    assert uc._post_eng_to_phys == pytac.units.unit_function
    assert uc._pre_phys_to_eng == pytac.units.unit_function
    m = mock.Mock()
    uc.set_pre_phys_to_eng(m)
    assert uc._post_eng_to_phys == pytac.units.unit_function
    assert uc._pre_phys_to_eng == m


def test_identity_conversion():
    id_conversion = PolyUnitConv([1, 0])
    physics_value = id_conversion.eng_to_phys(4)
    machine_value = id_conversion.phys_to_eng(4)
    assert machine_value == 4
    assert physics_value == 4


def test_linear_conversion():
    linear_conversion = PolyUnitConv([2, 3])
    physics_value = linear_conversion.convert(4, pytac.ENG, pytac.PHYS)
    machine_value = linear_conversion.convert(5, pytac.PHYS, pytac.ENG)
    assert physics_value == 11
    assert machine_value == 1


def test_quadratic_conversion():
    quadratic_conversion = PolyUnitConv([1, 2, 3])
    physics_value = quadratic_conversion.eng_to_phys(4)
    assert physics_value == 27
    with pytest.raises(pytac.exceptions.UnitsException):
        quadratic_conversion.convert(2.5, pytac.PHYS, pytac.ENG)


def test_poly_unit_conv_removes_imaginary_roots():
    poly_uc = PolyUnitConv([1, -3, 4])
    with pytest.raises(pytac.exceptions.UnitsException):
        poly_uc.convert(1, pytac.PHYS, pytac.ENG)


def test_ppconversion_to_physics_2_points():
    pchip_uc = PchipUnitConv([1, 3], [1, 3])
    assert pchip_uc.eng_to_phys(1) == 1
    assert pchip_uc.eng_to_phys(2) == 2
    assert pchip_uc.eng_to_phys(3) == 3


def test_pp_conversion_to_physics_3_points():
    pchip_uc = PchipUnitConv([1, 3, 5], [1, 3, 6])
    assert pchip_uc.eng_to_phys(1) == 1
    assert numpy.round(pchip_uc.eng_to_phys(2), 4) == 1.8875
    assert pchip_uc.eng_to_phys(3) == 3
    assert numpy.round(pchip_uc.eng_to_phys(4), 4) == 4.3625
    assert pchip_uc.eng_to_phys(5) == 6


def test_pp_conversion_to_machine_2_points():
    pchip_uc = PchipUnitConv([1, 3], [1, 3])
    assert pchip_uc.phys_to_eng(1) == 1
    assert pchip_uc.phys_to_eng(1.5) == 1.5


def test_PchipInterpolator_raises_ValueError_if_x_not_monotonically_increasing():
    with pytest.raises(ValueError):
        PchipUnitConv([1, 3, 2], [1, 2, 3])
    with pytest.raises(ValueError):
        PchipUnitConv([-1, -2, -3], [-1, -2, -3])


def test_PchipInterpolator_raises_ValueError_if_y_not_monotonic():
    with pytest.raises(ValueError):
        PchipUnitConv([1, 2, 3], [1, 3, 2])


def test_PchipUnitConv_with_solution_outside_bounds_raises_UnitsException():
    # This is a linear relationship, but the root is 0, outside of the
    # range of measurements.
    pchip_uc = PchipUnitConv((1, 2, 3), (1, 2, 3))
    with pytest.raises(pytac.exceptions.UnitsException):
        pchip_uc.phys_to_eng(0)


def test_PchipUnitConv_with_additional_function():
    pchip_uc = PchipUnitConv([2, 4], [2, 4], f1, f2)
    assert pchip_uc.eng_to_phys(2) == 4.0
    assert pchip_uc.eng_to_phys(3) == 6.0
    assert pchip_uc.phys_to_eng(4.0) == 2
    assert pchip_uc.phys_to_eng(6.0) == 3


def test_PolyUnitConv_with_additional_function():
    poly_uc = PolyUnitConv([2, 3], f1, f2)
    assert poly_uc.eng_to_phys(4) == 22.0
    assert poly_uc.eng_to_phys(5) == 26.0
    assert poly_uc.eng_to_phys(3) == 18.0
    assert poly_uc.phys_to_eng(22.0) == 4
    assert poly_uc.phys_to_eng(26.0) == 5
    assert poly_uc.phys_to_eng(18.0) == 3


def test_NullUnitConv():
    null_uc = NullUnitConv()
    assert null_uc.eng_to_phys(DUMMY_VALUE_1) == DUMMY_VALUE_1
    assert null_uc.eng_to_phys(DUMMY_VALUE_2) == DUMMY_VALUE_2
    assert null_uc.eng_to_phys(DUMMY_VALUE_3) == DUMMY_VALUE_3
    assert null_uc.phys_to_eng(DUMMY_VALUE_1) == DUMMY_VALUE_1
    assert null_uc.phys_to_eng(DUMMY_VALUE_2) == DUMMY_VALUE_2
    assert null_uc.phys_to_eng(DUMMY_VALUE_3) == DUMMY_VALUE_3
