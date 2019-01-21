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
    uc = UnitConv()
    with pytest.raises(NotImplementedError):
        uc.phys_to_eng(10)
    with pytest.raises(NotImplementedError):
        uc.eng_to_phys(-11)


@pytest.mark.parametrize('origin, target', [(pytac.LIVE, pytac.ENG),
                                            (pytac.PHYS, pytac.SP),
                                            ('a', 'b')])
def test_UnitConv_requires_correct_arguments(origin, target):
    uc = UnitConv()
    with pytest.raises(pytac.exceptions.UnitsException):
        uc.convert(10, origin, target)


def test_identity_conversion():
    id_conversion = PolyUnitConv([1, 0])
    physics_value = id_conversion.eng_to_phys(4)
    machine_value = id_conversion.phys_to_eng(4)
    assert machine_value == 4
    assert physics_value == 4


def test_linear_conversion():
    linear_conversion = PolyUnitConv([2, 3])
    physics_value = linear_conversion.eng_to_phys(4)
    machine_value = linear_conversion.phys_to_eng(5)
    assert physics_value == 11
    assert machine_value == 1


def test_linear_conversion_specifying_units():
    linear_conversion = PolyUnitConv([2, 3])
    physics_value = linear_conversion.convert(4, pytac.ENG, pytac.PHYS)
    assert physics_value == 11
    machine_value = linear_conversion.convert(5, pytac.PHYS, pytac.ENG)
    assert machine_value == 1


def test_quadratic_conversion():
    quadratic_conversion = PolyUnitConv([1, 2, 3])
    physics_value = quadratic_conversion.eng_to_phys(4)
    assert physics_value == 27
    with pytest.raises(pytac.exceptions.UnitsException):
        quadratic_conversion.phys_to_eng(2.5)


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
