import math
import scipy.constants


electron_mass_name = 'electron mass energy equivalent in MeV'
electron_mass_mev, _, _ = scipy.constants.physical_constants[electron_mass_name]


def rigidity(energy_mev):
    gamma = energy_mev / electron_mass_mev
    beta = math.sqrt(1 - gamma ** (-2))
    energy_j = energy_mev * 1e6 * scipy.constants.e
    p = beta * energy_j / scipy.constants.c
    return p / scipy.constants.e
