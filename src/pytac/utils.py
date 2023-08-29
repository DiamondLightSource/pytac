"""Utility functions."""
import math
from typing import Callable

import scipy.constants

electron_mass_name = "electron mass energy equivalent in MeV"
electron_mass_mev, _, _ = scipy.constants.physical_constants[electron_mass_name]


def get_rigidity(energy_mev: int) -> float:
    """Get rigidity function.

    Args:
        energy_mev: the energy of the lattice.

    Returns:
        p devided by the elementary charge.
    """
    gamma = energy_mev / electron_mass_mev
    beta = math.sqrt(1 - gamma ** (-2))
    energy_j = energy_mev * 1e6 * scipy.constants.e
    p = beta * energy_j / scipy.constants.c
    return p / scipy.constants.e


def get_div_rigidity(energy: int) -> Callable[[int], float]:
    """Return the function div_rigidity.

    Args:
        energy: the energy of the lattice.

    Returns:
        div rigidity.
    """
    rigidity = get_rigidity(energy)

    def div_rigidity(value):
        return value / rigidity

    return div_rigidity


def get_mult_rigidity(energy: int) -> Callable[[int], float]:
    """Return the function mult_rigidity.

    Args:
        energy: the energy of the lattice.

    Returns:
        mult rigidity.
    """
    rigidity = get_rigidity(energy)

    def mult_rigidity(value):
        return value * rigidity

    return mult_rigidity
