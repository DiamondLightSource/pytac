"""Module to load the elements of the machine from csv files.

The csv files are stored in one directory with specified names:

 * elements.csv
 * devices.csv
 * families.csv
 * unitconv.csv
 * uc_poly_data.csv
 * uc_pchip_data.csv
"""
import collections
import copy
import csv
import os

import pytac
from pytac import data_source, device, element, lattice, units, utils
from pytac.exceptions import ControlSystemException


# Create a default unit conversion object that returns the input unchanged.
DEFAULT_UC = units.NullUnitConv()

ELEMENTS_FILENAME = 'elements.csv'
DEVICES_FILENAME = 'devices.csv'
FAMILIES_FILENAME = 'families.csv'
UNITCONV_FILENAME = 'unitconv.csv'
POLY_FILENAME = 'uc_poly_data.csv'
PCHIP_FILENAME = 'uc_pchip_data.csv'


def load_poly_unitconv(filename):
    """Load polynomial unit conversions from a csv file.

    Args:
        filename (path-like object): The pathname of the file from which to
                                      load the polynomial unit conversions.

    Returns:
        dict: A dictionary of the unit conversions.
    """
    unitconvs = {}
    data = collections.defaultdict(list)
    with open(filename) as poly:
        csv_reader = csv.DictReader(poly)
        for item in csv_reader:
            data[(int(item['uc_id']))].append((int(item['coeff']),
                                               float(item['val'])))
    # Create PolyUnitConv for each item and put in the dict
    for uc_id in data:
        u = units.PolyUnitConv(
            [x[1] for x in reversed(sorted(data[uc_id]))], name=uc_id
        )
        unitconvs[uc_id] = u
    return unitconvs


def load_pchip_unitconv(filename):
    """Load pchip unit conversions from a csv file.

    Args:
        filename (path-like object): The pathname of the file from which to
                                      load the pchip unit conversions.

    Returns:
        dict: A dictionary of the unit conversions.
    """
    unitconvs = {}
    data = collections.defaultdict(list)
    with open(filename) as pchip:
        csv_reader = csv.DictReader(pchip)
        for item in csv_reader:
            data[(int(item['uc_id']))].append((float(item['eng']),
                                               float(item['phy'])))
    # Create PchipUnitConv for each item and put in the dict
    for uc_id in data:
        eng = [x[0] for x in sorted(data[uc_id])]
        phy = [x[1] for x in sorted(data[uc_id])]
        u = units.PchipUnitConv(eng, phy, name=uc_id)
        unitconvs[uc_id] = u
    return unitconvs


def load_unitconv(directory, mode, lattice):
    """Load the unit conversion objects from a file.

    Args:
        directory (str): The directory where the data is stored.
        mode (str): The name of the mode that is used.
        lattice(Lattice): The lattice object that will be used.
    """
    unitconvs = {}
    # Assemble datasets from the polynomial file
    poly_file = os.path.join(directory, mode, POLY_FILENAME)
    unitconvs.update(load_poly_unitconv(poly_file))
    # Assemble datasets from the pchip file
    pchip_file = os.path.join(directory, mode, PCHIP_FILENAME)
    unitconvs.update(load_pchip_unitconv(pchip_file))
    # Add the unitconv objects to the elements
    with open(os.path.join(directory, mode, UNITCONV_FILENAME)) as unitconv:
        csv_reader = csv.DictReader(unitconv)
        for item in csv_reader:
            # Special case for element 0: the lattice itself.
            if int(item['el_id']) == 0:
                if item['uc_type'] != 'null':
                    # Each element needs its own unitconv object as
                    # it may for example have different limit.
                    uc = copy.copy(unitconvs[int(item['uc_id'])])
                    uc.phys_units = item['phys_units']
                    uc.eng_units = item['eng_units']
                    if item['lower_lim'] != '':
                        uc.set_conversion_limits(float(item['lower_lim']),
                                                 float(item['upper_lim']))
                else:
                    uc = units.NullUnitConv(item['eng_units'],
                                            item['phys_units'])
                lattice.set_unitconv(item['field'], uc)
            else:
                element = lattice[int(item['el_id']) - 1]
                # For certain magnet types, we need an additional rigidity
                # conversion factor as well as the raw conversion.
                if item['uc_type'] == 'null':
                    uc = units.NullUnitConv(item['eng_units'],
                                            item['phys_units'])
                else:
                    # Each element needs its own unitconv object as
                    # it may for example have different limit.
                    uc = copy.copy(unitconvs[int(item['uc_id'])])
                    if element.families.intersection(('HSTR', 'VSTR', 'QUAD',
                                                      'SEXT', 'BEND')):
                        energy = lattice.get_value('energy', units=pytac.PHYS)
                        uc.set_post_eng_to_phys(utils.get_div_rigidity(energy))
                        uc.set_pre_phys_to_eng(utils.get_mult_rigidity(energy))
                    uc.phys_units = item['phys_units']
                    uc.eng_units = item['eng_units']
                    if item['lower_lim'] != '':
                        uc.set_conversion_limits(float(item['lower_lim']),
                                                 float(item['upper_lim']))
                element.set_unitconv(item['field'], uc)


def load(mode, control_system=None, directory=None, symmetry=None):
    """Load the elements of a lattice from a directory.

    Args:
        mode (str): The name of the mode to be loaded.
        control_system (ControlSystem): The control system to be used. If none
                                         is provided an EpicsControlSystem will
                                         be created.
        directory (str): Directory where to load the files from. If no
                          directory is given the data directory at the root of
                          the repository is used.
        symmetry (int): The symmetry of the lattice (the number of cells).

    Returns:
        Lattice: The lattice containing all elements.

    Raises:
        ControlSystemException: if the default control system, cothread, is not
                                 installed.
    """
    try:
        if control_system is None:
            # Don't import epics unless we need it to avoid unnecessary
            # installation of cothread
            from pytac import cothread_cs
            control_system = cothread_cs.CothreadControlSystem()
    except ImportError:
        raise ControlSystemException("Please install cothread to load a "
                                     "lattice using the default control "
                                     "system (found in cothread_cs.py).")
    if directory is None:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'data')
    lat = lattice.EpicsLattice(mode, control_system, symmetry=symmetry)
    lat.set_data_source(data_source.DeviceDataSource(), pytac.LIVE)
    with open(os.path.join(directory, mode, ELEMENTS_FILENAME)) as elements:
        csv_reader = csv.DictReader(elements)
        for item in csv_reader:
            name = item['name'] if item['name'] != '' else None
            e = element.EpicsElement(float(item['length']), item['type'],
                                     name, lat)
            e.add_to_family(item['type'])
            e.set_data_source(data_source.DeviceDataSource(), pytac.LIVE)
            lat.add_element(e)
    with open(os.path.join(directory, mode, DEVICES_FILENAME)) as devices:
        csv_reader = csv.DictReader(devices)
        for item in csv_reader:
            name = item['name']
            get_pv = item['get_pv'] if item['get_pv'] else None
            set_pv = item['set_pv'] if item['set_pv'] else None
            pve = True
            d = device.EpicsDevice(name, control_system, pve, get_pv, set_pv)
            # Devices on index 0 are attached to the lattice not elements.
            if int(item['el_id']) == 0:
                lat.add_device(item['field'], d, DEFAULT_UC)
            else:
                lat[int(item['el_id']) - 1].add_device(item['field'], d,
                                                       DEFAULT_UC)
        # Add basic devices to the lattice.
        positions = []
        for elem in lat:
            positions.append(elem.s)
        lat.add_device('s_position', device.BasicDevice(positions), DEFAULT_UC)
        lat.add_device('energy', device.BasicDevice(3.e+09), DEFAULT_UC)
    with open(os.path.join(directory, mode, FAMILIES_FILENAME)) as families:
        csv_reader = csv.DictReader(families)
        for item in csv_reader:
            lat[int(item['el_id']) - 1].add_to_family(item['family'])
    if os.path.exists(os.path.join(directory, mode, UNITCONV_FILENAME)):
        load_unitconv(directory, mode, lat)
    return lat
