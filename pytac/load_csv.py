import os
import csv
from pytac import lattice, element, device, units, utils
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
        directory(string): The directory where the data is stored.
        mode(string): The name of the mode that is used.
        lattice(Lattice): The lattice object that will be used.
    """
    data = collections.defaultdict(list)
    uc = {}
    with open(os.path.join(directory, mode, 'uc_poly_data.csv')) as poly:
        csv_reader = csv.DictReader(poly)
        for item in csv_reader:
            data[(int(item['uc_id']))].append((int(item['coeff']), float(item['val'])))

    for d in data:
        u = units.PolyUnitConv([x[1] for x in reversed(sorted(data[d]))])
        uc[d] = u
    data.clear()
    with open(os.path.join(directory, mode, 'uc_pchip_data.csv')) as pchip:
        csv_reader = csv.DictReader(pchip)
        for item in csv_reader:
            data[(int(item['uc_id']))].append((float(item['eng']), float(item['phy'])))

    for d in data:
        eng = [x[0] for x in sorted(data[d])]
        phy = [x[1] for x in sorted(data[d])]
        u = units.PchipUnitConv(eng, phy)
        uc[d] = u

    with open(os.path.join(directory, mode, 'unitconv.csv')) as unitconv:
        csv_reader = csv.DictReader(unitconv)
        for item in csv_reader:
            element = lattice[int(item['el_id']) - 1]
            if 'QUAD' in element.families or 'SEXT' in element.families:
                uc[int(item['uc_id'])].f1 = get_div_rigidity(lattice.get_energy())
                uc[int(item['uc_id'])].f2 = get_mult_rigidity(lattice.get_energy())
            element._uc[item['field']] = uc[int(item['uc_id'])]


def load(mode, control_system, directory=None):
    """Load the elements of a lattice from a directory.

    Args:
        mode(string): The name of the mode to be loaded.
        control_system(ControlSystem): The control system to be used.
        directory(string): Directory where to load the files from. If no directory is given
            that the data directory at the root of the repository is used.

    Returns:
        Lattice: The lattice containing all elements.
    """
    if directory is None:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    lat = lattice.Lattice(mode, control_system, 3000)
    with open(os.path.join(directory, mode, 'elements.csv')) as elements:
        csv_reader = csv.DictReader(elements)
        for item in csv_reader:
            e = element.Element(item['name'], float(item['length']),
                                item['type'])
            e.add_to_family(item['type'])
            lat.add_element(e)

    with open(os.path.join(directory, mode, 'devices.csv')) as devices:
        csv_reader = csv.DictReader(devices)
        for item in csv_reader:
            enable_pv = item['enable_pv']
            enable_value = item['enable_value']
            get_pv = item['get_pv']
            set_pv = item['set_pv']
            pve = True
            if enable_pv and enable_value:
                pve = device.PvEnabler(enable_pv, enable_value, control_system)
            d = device.Device(control_system, pve, get_pv, set_pv)
            lat[int(item['id']) - 1].add_device(item['field'], d, control_system)

    with open(os.path.join(directory, mode, 'families.csv')) as families:
        csv_reader = csv.DictReader(families)
        for item in csv_reader:
            lat[int(item['id']) - 1].add_to_family(item['family'])

    if os.path.exists(os.path.join(directory, mode, 'unitconv.csv')):
        load_unitconv(directory, mode, lat)

    return lat
