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
import contextlib
import copy
import csv
from pathlib import Path
from typing import Dict, Iterator

import pytac
from pytac import data_source, element, utils
from pytac.device import EpicsDevice, SimpleDevice
from pytac.exceptions import ControlSystemException
from pytac.lattice import EpicsLattice, Lattice
from pytac.units import NullUnitConv, PchipUnitConv, PolyUnitConv, UnitConv

# Create a default unit conversion object that returns the input unchanged.
DEFAULT_UC = NullUnitConv()

ELEMENTS_FILENAME = "elements.csv"
EPICS_DEVICES_FILENAME = "epics_devices.csv"
SIMPLE_DEVICES_FILENAME = "simple_devices.csv"
FAMILIES_FILENAME = "families.csv"
UNITCONV_FILENAME = "unitconv.csv"
POLY_FILENAME = "uc_poly_data.csv"
PCHIP_FILENAME = "uc_pchip_data.csv"


@contextlib.contextmanager
def csv_loader(csv_file: Path) -> Iterator[csv.DictReader]:
    with open(csv_file) as f:
        csv_reader = csv.DictReader(f)
        yield csv_reader


def load_poly_unitconv(filepath: Path) -> Dict[int, PolyUnitConv]:
    """Load polynomial unit conversions from a csv file.

    Args:
        filepath: The file from which to load.

    Returns:
        dict: A dictionary of the unit conversions.
    """
    unitconvs: Dict[int, PolyUnitConv] = {}
    data = collections.defaultdict(list)
    with csv_loader(filepath) as csv_reader:
        for item in csv_reader:
            data[(int(item["uc_id"]))].append((int(item["coeff"]), float(item["val"])))
    # Create PolyUnitConv for each item and put in the dict
    for uc_id in data:
        u = PolyUnitConv([x[1] for x in reversed(sorted(data[uc_id]))], name=uc_id)
        unitconvs[uc_id] = u
    return unitconvs


def load_pchip_unitconv(filepath: Path) -> Dict[int, PchipUnitConv]:
    """Load pchip unit conversions from a csv file.

    Args:
        filename: The file from which to load.

    Returns:
        dict: A dictionary of the unit conversions.
    """
    unitconvs: Dict[int, PchipUnitConv] = {}
    data = collections.defaultdict(list)
    with csv_loader(filepath) as csv_reader:
        for item in csv_reader:
            data[(int(item["uc_id"]))].append((float(item["eng"]), float(item["phy"])))
    # Create PchipUnitConv for each item and put in the dict
    for uc_id in data:
        eng = [x[0] for x in sorted(data[uc_id])]
        phy = [x[1] for x in sorted(data[uc_id])]
        u = PchipUnitConv(eng, phy, name=uc_id)
        unitconvs[uc_id] = u
    return unitconvs


def load_unitconv(mode_dir: Path, lattice: Lattice) -> None:
    """Load the unit conversion objects from a file.

    Args:
        mode_dir: Path to directory containing CSV files.
        lattice: The lattice object that will be used.
    """
    unitconvs: Dict[int, UnitConv] = {}
    # Assemble datasets from the polynomial file
    unitconvs.update(load_poly_unitconv(mode_dir / POLY_FILENAME))
    # Assemble datasets from the pchip file
    unitconvs.update(load_pchip_unitconv(mode_dir / PCHIP_FILENAME))
    # Add the unitconv objects to the elements
    with csv_loader(mode_dir / UNITCONV_FILENAME) as csv_reader:
        for item in csv_reader:
            # Special case for element 0: the lattice itself.
            if int(item["el_id"]) == 0:
                if item["uc_type"] != "null":
                    # Each element needs its own unitconv object as
                    # it may for example have different limit.
                    uc = copy.copy(unitconvs[int(item["uc_id"])])
                    uc.phys_units = item["phys_units"]
                    uc.eng_units = item["eng_units"]
                    upper, lower = (
                        float(lim) if lim != "" else None
                        for lim in [item["upper_lim"], item["lower_lim"]]
                    )
                    uc.set_conversion_limits(lower, upper)
                else:
                    uc = NullUnitConv(item["eng_units"], item["phys_units"])
                lattice.set_unitconv(item["field"], uc)
            else:
                element = lattice[int(item["el_id"]) - 1]
                # For certain magnet types, we need an additional rigidity
                # conversion factor as well as the raw conversion.
                if item["uc_type"] == "null":
                    uc = NullUnitConv(item["eng_units"], item["phys_units"])
                else:
                    # Each element needs its own unitconv object as
                    # it may for example have different limit.
                    uc = copy.copy(unitconvs[int(item["uc_id"])])
                    if any(
                        element.is_in_family(f)
                        for f in ("HSTR", "VSTR", "Quadrupole", "Sextupole", "Bend")
                    ):
                        energy = lattice.get_value("energy", units=pytac.PHYS)
                        uc.set_post_eng_to_phys(utils.get_div_rigidity(energy))
                        uc.set_pre_phys_to_eng(utils.get_mult_rigidity(energy))
                    uc.phys_units = item["phys_units"]
                    uc.eng_units = item["eng_units"]
                    upper, lower = (
                        float(lim) if lim != "" else None
                        for lim in [item["upper_lim"], item["lower_lim"]]
                    )
                    uc.set_conversion_limits(lower, upper)
                element.set_unitconv(item["field"], uc)


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
        raise ControlSystemException(
            "Please install cothread to load a "
            "lattice using the default control "
            "system (found in cothread_cs.py)."
        )
    if directory is None:
        directory = Path(__file__).resolve().parent / "data"
    mode_dir = directory / mode
    lat = EpicsLattice(mode, control_system, symmetry=symmetry)
    lat.set_data_source(data_source.DeviceDataSource(), pytac.LIVE)
    with csv_loader(mode_dir / ELEMENTS_FILENAME) as csv_reader:
        for item in csv_reader:
            name = item["name"] if item["name"] != "" else None
            e = element.EpicsElement(float(item["length"]), item["type"], name, lat)
            e.add_to_family(item["type"])
            e.set_data_source(data_source.DeviceDataSource(), pytac.LIVE)
            lat.add_element(e)
    with csv_loader(mode_dir / EPICS_DEVICES_FILENAME) as csv_reader:
        for item in csv_reader:
            name = item["name"]
            index = int(item["el_id"])
            get_pv = item["get_pv"] if item["get_pv"] else None
            set_pv = item["set_pv"] if item["set_pv"] else None
            pve = True
            d = EpicsDevice(name, control_system, pve, get_pv, set_pv)
            # Devices on index 0 are attached to the lattice not elements.
            target = lat if index == 0 else lat[index - 1]
            target.add_device(item["field"], d, DEFAULT_UC)
        # Add basic devices to the lattice.
        positions = []
        for elem in lat:
            positions.append(elem.s)
        lat.add_device("s_position", SimpleDevice(positions, readonly=True), True)
    simple_devices_file = mode_dir / SIMPLE_DEVICES_FILENAME
    if simple_devices_file.exists():
        with csv_loader(simple_devices_file) as csv_reader:
            for item in csv_reader:
                index = int(item["el_id"])
                field = item["field"]
                value = float(item["value"])
                readonly = item["readonly"].lower() == "true"
                # Devices on index 0 are attached to the lattice not elements.
                target = lat if index == 0 else lat[index - 1]
                target.add_device(field, SimpleDevice(value, readonly=readonly), True)
    with csv_loader(mode_dir / FAMILIES_FILENAME) as csv_reader:
        for item in csv_reader:
            lat[int(item["el_id"]) - 1].add_to_family(item["family"])
    unitconv_file = mode_dir / UNITCONV_FILENAME
    if unitconv_file.exists():
        load_unitconv(mode_dir, lat)
    return lat
