"""Module to load the elements of the machine from multiple csv files stored in the same directory."""
from __future__ import print_function
import sys
import os
import csv
import pytac
from pytac import lattice, element, device, model, units, utils
import collections


def get_div_rigidity(energy):
    rigidity = utils.rigidity(energy)

    def div_rigidity(input):
        return input / rigidity

    return div_rigidity


def get_mult_rigidity(energy):
    rigidity = utils.rigidity(energy)

    def mult_rigidity(input):
        return input * rigidity

    return mult_rigidity


def load_unitconv(directory, mode, lattice):
    """Load the unit conversion objects from a file.

    Args:
        directory (str): The directory where the data is stored.
        mode (str): The name of the mode that is used.
        lattice(Lattice): The lattice object that will be used.
    """
    data = collections.defaultdict(list)
    unitconvs = {}
    # Assemble datasets from the polynomial file
    with open(os.path.join(directory, mode, 'uc_poly_data.csv')) as poly:
        csv_reader = csv.DictReader(poly)
        for item in csv_reader:
            data[(int(item['uc_id']))].append((int(item['coeff']), float(item['val'])))
    # Create PolyUnitConv for each item and put in the dict
    for uc_id in data:
        u = units.PolyUnitConv([x[1] for x in reversed(sorted(data[uc_id]))])
        unitconvs[uc_id] = u
    data.clear()

    # Assemble datasets from the pchip file.
    with open(os.path.join(directory, mode, 'uc_pchip_data.csv')) as pchip:
        csv_reader = csv.DictReader(pchip)
        for item in csv_reader:
            data[(int(item['uc_id']))].append((float(item['eng']), float(item['phy'])))

    # Create PchipUnitConv for each item and put in the dict
    for uc_id in data:
        eng = [x[0] for x in sorted(data[uc_id])]
        phy = [x[1] for x in sorted(data[uc_id])]
        u = units.PchipUnitConv(eng, phy)
        unitconvs[uc_id] = u

    with open(os.path.join(directory, mode, 'unitconv.csv')) as unitconv:
        csv_reader = csv.DictReader(unitconv)
        for item in csv_reader:
            element = lattice[int(item['el_id']) - 1]
            # For certain magnet types, we need an additional rigidity
            # conversion factor as well as the raw conversion.
            if element.families.intersection(('HSTR', 'VSTR', 'QUAD', 'SEXT')):
                unitconvs[int(item['uc_id'])]._post_eng_to_phys = get_div_rigidity(lattice.get_energy())
                unitconvs[int(item['uc_id'])]._pre_phys_to_eng = get_mult_rigidity(lattice.get_energy())
            element._uc[item['field']] = unitconvs[int(item['uc_id'])]


def load(mode, control_system=None, directory=None):
    """Load the elements of a lattice from a directory.

    Args:
        mode (str): The name of the mode to be loaded.
        control_system (ControlSystem): The control system to be used. If none is provided
            an EpicsControlSystem will be created.
        directory (str): Directory where to load the files from. If no directory is given
            the data directory at the root of the repository is used.

    Returns:
        Lattice: The lattice containing all elements.
    """
    try:
        if control_system is None:
            # Don't import epics unless we need it to avoid unnecessary
            # installation of cothread
            from pytac import epics
            control_system = epics.EpicsControlSystem()
    except ImportError:
        print(('To load a lattice using the default control system,'
                ' please install cothread.'),
              file=sys.stderr)
        return None
    if directory is None:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'data')
    lat = lattice.Lattice(mode, control_system, 3000)
    s = 0
    index = 1
    with open(os.path.join(directory, mode, 'elements.csv')) as elements:
        csv_reader = csv.DictReader(elements)
        for item in csv_reader:
            length = float(item['length'])
            cell = int(item['cell']) if item['cell'] else None
            e = element.Element(item['name'], length,
                                item['type'], s, index, cell)
            e.add_to_family(item['type'])
            e.set_model(model.DeviceModel(), pytac.LIVE)
            lat.add_element(e)
            s += length
            index += 1

    with open(os.path.join(directory, mode, 'devices.csv')) as devices:
        csv_reader = csv.DictReader(devices)
        for item in csv_reader:
            name = item['name']
            get_pv = item['get_pv'] if item['get_pv'] else None
            set_pv = item['set_pv'] if item['set_pv'] else None
            pve = True
            d = device.Device(name, control_system, pve, get_pv, set_pv)
            lat[int(item['id']) - 1].add_device(item['field'], d, units.UnitConv())

    with open(os.path.join(directory, mode, 'families.csv')) as families:
        csv_reader = csv.DictReader(families)
        for item in csv_reader:
            lat[int(item['id']) - 1].add_to_family(item['family'])

    if os.path.exists(os.path.join(directory, mode, 'unitconv.csv')):
        load_unitconv(directory, mode, lat)

    return lat
