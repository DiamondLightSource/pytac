"""Utility functions."""
import math
from typing import Any, Callable

import scipy.constants

electron_mass_name = "electron mass energy equivalent in MeV"
electron_mass_mev, _, _ = scipy.constants.physical_constants[electron_mass_name]


def get_rigidity(energy_mev: Any) -> float:
    """Get rigidity function.

    N.B. energy_mev should be of type: float, but this cannot be implimented with
        the current code structure.

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


def get_div_rigidity(energy: Any) -> Callable[[float], float]:
    """Return the function div_rigidity.

    N.B. energy should be of type: float, but this cannot be implimented with
        the current code structure.

    Args:
        energy: the energy of the lattice.

    Returns:
        div rigidity.
    """
    rigidity = get_rigidity(energy)

    def div_rigidity(value: float) -> float:
        return value / rigidity

    return div_rigidity


def get_mult_rigidity(energy: Any) -> Callable[[float], float]:
    """Return the function mult_rigidity.

    N.B. energy should be of type: float, but this cannot be implimented with
        the current code structure.

    Args:
        energy: the energy of the lattice.

    Returns:
        mult rigidity.
    """
    rigidity = get_rigidity(energy)

    def mult_rigidity(value: float) -> float:
        return value * rigidity

    return mult_rigidity
