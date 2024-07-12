"""Utility functions."""

import math

import scipy.constants

electron_mass_name = "electron mass energy equivalent in MeV"
electron_mass_mev, _, _ = scipy.constants.physical_constants[electron_mass_name]


def get_rigidity(energy_mev):
    """
    Args:
        energy_mev (int): the energy of the lattice.

    Returns:
        float: p devided by the elementary charge.
    """
    gamma = energy_mev / electron_mass_mev
    beta = math.sqrt(1 - gamma ** (-2))
    energy_j = energy_mev * 1e6 * scipy.constants.e
    p = beta * energy_j / scipy.constants.c
    return p / scipy.constants.e


def get_div_rigidity(energy):
    """
    Args:
        energy (int): the energy of the lattice.

    Returns:
        function: div rigidity.
    """
    rigidity = get_rigidity(energy)

    def div_rigidity(value):
        return value / rigidity

    return div_rigidity


def get_mult_rigidity(energy):
    """
    Args:
        energy (int): the energy of the lattice.

    Returns:
        function: mult rigidity.
    """
    rigidity = get_rigidity(energy)

    def mult_rigidity(value):
        return value * rigidity

    return mult_rigidity
