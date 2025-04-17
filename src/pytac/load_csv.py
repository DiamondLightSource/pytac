"""Module to load the elements of the machine from csv files.

The csv files are stored in one directory with specified names:

 * elements.csv
 * devices.csv
 * families.csv
 * unitconv.csv
 * uc_poly_data.csv
 * uc_pchip_data.csv
"""

import ast
import collections
import contextlib
import copy
import csv
import logging
import os
from collections.abc import Iterator
from pathlib import Path

import pytac
from pytac import data_source, element, utils
from pytac.device import EpicsDevice, SimpleDevice
from pytac.exceptions import ControlSystemException, UnitsException
from pytac.lattice import EpicsLattice, Lattice
from pytac.units import NullUnitConv, PchipUnitConv, PolyUnitConv, UnitConv

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


def load_poly_unitconv(filepath: Path) -> dict[int, PolyUnitConv]:
    """Load polynomial unit conversions from a csv file.

    Args:
        filepath: The file from which to load.

    Returns:
        dict: A dictionary of the unit conversions.
    """
    unitconvs: dict[int, PolyUnitConv] = {}
    data = collections.defaultdict(list)
    with csv_loader(filepath) as csv_reader:
        for item in csv_reader:
            data[(int(item["uc_id"]))].append((int(item["coeff"]), float(item["val"])))
    # Create PolyUnitConv for each item and put in the dict
    for uc_id in data:
        u = PolyUnitConv([x[1] for x in sorted(data[uc_id], reverse=True)], name=uc_id)
        unitconvs[uc_id] = u
    return unitconvs


def load_pchip_unitconv(filepath: Path) -> dict[int, PchipUnitConv]:
    """Load pchip unit conversions from a csv file.

    Args:
        filename: The file from which to load.

    Returns:
        dict: A dictionary of the unit conversions.
    """
    unitconvs: dict[int, PchipUnitConv] = {}
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


def resolve_unitconv(
    uc_params: dict, unitconvs: dict, polyconv_file: Path, pchipconv_file: Path
) -> UnitConv:
    """Create a unit conversion object based on the dictionary of parameters passed.

    Args:
        uc_params (Dict): A dictionary of parameters specifying the unit conversion
                           object's properties.
        unitconvs (Dict): A dictionary of all loaded unit conversion objects.
        polyconv_file (Path): The path to the .csv file from which all PolyUnitConv
                               objects are loaded.
        pchipconv_file (Path): The path to the .csv file from which all PchipUnitConv
                                objects are loaded.
    Returns:
        UnitConv: The unit conversion object as specified by uc_params.

    Raises:
        UnitsException: if the "uc_id" given in uc_params isn't in the unitconvs Dict.
    """
    error_msg = (
        f"Unable to resolve {uc_params['uc_type']} unit conversion with ID "
        f"{uc_params['uc_id']}, "
    )
    if uc_params["uc_type"] == "null":
        uc = NullUnitConv(uc_params["eng_units"], uc_params["phys_units"])
    else:
        # Each element needs its own UnitConv object as it may have different limits.
        try:
            uc = copy.copy(unitconvs[int(uc_params["uc_id"])])
        except KeyError:
            if uc_params["uc_type"] == "poly" and not polyconv_file.exists():
                raise UnitsException(
                    error_msg + f"{polyconv_file} not found."
                ) from KeyError
            elif uc_params["uc_type"] == "pchip" and not pchipconv_file.exists():
                raise UnitsException(
                    error_msg + f"{pchipconv_file} not found."
                ) from KeyError
            else:
                raise UnitsException(
                    error_msg + "unrecognised UnitConv type."
                ) from KeyError
        uc.phys_units = uc_params["phys_units"]
        uc.eng_units = uc_params["eng_units"]
        lower, upper = [
            float(lim) if lim != "" else None
            for lim in [uc_params["lower_lim"], uc_params["upper_lim"]]
        ]
        uc.set_conversion_limits(lower, upper)
    return uc


async def load_unitconv(mode_dir: Path, lattice: Lattice) -> None:
    """Load the unit conversion objects from a file.

    Args:
        mode_dir: Path to directory containing CSV files.
        lattice: The lattice object that will be used.
    """
    unitconvs: dict[int, UnitConv] = {}
    # Assemble datasets from the polynomial file
    polyconv_file = mode_dir / POLY_FILENAME
    if polyconv_file.exists():
        unitconvs.update(load_poly_unitconv(polyconv_file))
    else:
        logging.warning(f"{polyconv_file} not found, unable to load PolyUnitConvs.")
    # Assemble datasets from the pchip file
    pchipconv_file = mode_dir / PCHIP_FILENAME
    if pchipconv_file.exists():
        unitconvs.update(load_pchip_unitconv(pchipconv_file))
    else:
        logging.warning(f"{pchipconv_file} not found, unable to load PchipUnitConvs.")
    # Add the unitconv objects to the elements
    with csv_loader(mode_dir / UNITCONV_FILENAME) as csv_reader:
        for item in csv_reader:
            uc = resolve_unitconv(item, unitconvs, polyconv_file, pchipconv_file)
            # Special case for element 0: the lattice itself.
            if int(item["el_id"]) == 0:
                lattice.set_unitconv(item["field"], uc)
            else:
                element = lattice[int(item["el_id"]) - 1]
                # For certain magnet types, we need an additional rigidity
                # conversion factor as well as the raw conversion.
                # TODO: This should probably be moved into the .csv files somewhere.
                rigidity_families = {
                    "hstr",
                    "vstr",
                    "quadrupole",
                    "sextupole",
                    "multipole",
                    "bend",
                }
                if item["uc_type"] != "null" and element._families & rigidity_families:  # noqa: SLF001
                    energy = await lattice.get_value("energy", units=pytac.ENG)
                    uc.set_post_eng_to_phys(utils.get_div_rigidity(energy))
                    uc.set_pre_phys_to_eng(utils.get_mult_rigidity(energy))
                element.set_unitconv(item["field"], uc)


async def load(
    mode, control_system=None, directory=None, symmetry=None
) -> EpicsLattice:
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

            control_system = cothread_cs.AIOCAControlSystem()
    except ImportError:
        raise ControlSystemException(
            "Please install cothread to load a lattice using the default control system"
            " (found in cothread_cs.py)."
        ) from ImportError
    if directory is None:
        directory = Path(__file__).resolve().parent / "data"
    mode_dir = directory / mode
    lat = EpicsLattice(mode, control_system, symmetry=symmetry)
    lat.set_data_source(data_source.DeviceDataSource(), pytac.LIVE)
    with csv_loader(mode_dir / ELEMENTS_FILENAME) as csv_reader:
        for item in csv_reader:
            name = item.get("name") or None  # Default to None if empty string
            e = element.EpicsElement(float(item["length"]), item["type"], name, lat)
            e.add_to_family(item["type"])
            e.set_data_source(data_source.DeviceDataSource(), pytac.LIVE)
            lat.add_element(e)
    with csv_loader(mode_dir / EPICS_DEVICES_FILENAME) as csv_reader:
        for item in csv_reader:
            index = int(item["el_id"])
            get_pv = item["get_pv"] if item["get_pv"] else None
            set_pv = item["set_pv"] if item["set_pv"] else None
            # Devices on index 0 are attached to the lattice not elements.
            target = lat if index == 0 else lat[index - 1]
            # Create with a default UnitConv that returns the input unchanged.
            target.add_device(  # type: ignore[attr-defined]
                item["field"],
                EpicsDevice(item["name"], control_system, rb_pv=get_pv, sp_pv=set_pv),
                NullUnitConv(),
            )
        # Add basic devices to the lattice.
        positions = []
        for elem in lat:  # type: ignore[attr-defined]
            positions.append(elem.s)
        lat.add_device(
            "s_position", SimpleDevice(positions, readonly=True), NullUnitConv()
        )
    simple_devices_file = mode_dir / SIMPLE_DEVICES_FILENAME
    if simple_devices_file.exists():
        with csv_loader(simple_devices_file) as csv_reader:
            for item in csv_reader:
                index = int(item["el_id"])
                try:
                    readonly = ast.literal_eval(item["readonly"])
                    assert isinstance(readonly, bool)
                except (ValueError, AssertionError) as e:
                    raise ValueError(
                        f"Unable to evaluate {item['readonly']} as a boolean."
                    ) from e
                # Devices on index 0 are attached to the lattice not elements.
                target = lat if index == 0 else lat[index - 1]
                # Create with a default UnitConv that returns the input unchanged.
                target.add_device(  # type: ignore[attr-defined]
                    item["field"],
                    SimpleDevice(float(item["value"]), readonly=readonly),
                    NullUnitConv(),
                )
    with csv_loader(mode_dir / FAMILIES_FILENAME) as csv_reader:
        for item in csv_reader:
            lat[int(item["el_id"]) - 1].add_to_family(item["family"])
    unitconv_file = mode_dir / UNITCONV_FILENAME
    if unitconv_file.exists():
        await load_unitconv(mode_dir, lat)
    return lat


def available_ringmodes(directory=None) -> set[str]:
    """Return the possible ringmodes based on the subdirectories and files in
    the given directory.

    .. Note:: It is not guaranteed that the modes returned will be able to be
       successfully loaded due to errors, missing data, etc. I.e., any mode
       that can be loaded will always be returned, but modes that can't be
       loaded might also sometimes be returned.

    Args:
        directory (str): The data directory to check inside. If no directory
                          is given the default data directory location is used.

    Returns:
        set[str]: A set of possible ringmodes.

    Raises:
        OSError: if no ringmodes can be found in the specified directory.
    """
    if directory is None:
        directory = Path(__file__).resolve().parent / "data"
    modes = set()
    for directory_object in os.scandir(directory):
        if directory_object.is_dir():
            contents = os.listdir(directory_object.path)
            if ELEMENTS_FILENAME in contents and FAMILIES_FILENAME in contents:
                modes.add(directory_object.name)
    if not modes:
        raise OSError(f"No ringmodes found in {os.path.realpath(directory)}")
    return modes
