""" This file tests the entire loading of the DLS machine from the CSV
    files in the data directory. These are more like integration tests,
    and allows us to check that the pytac setup is working correctly.
"""

import re
from unittest import mock

import numpy
import pytest
from pytest_lazyfixture import lazy_fixture

import pytac

EPS = 1e-8


def get_lattice(ring_mode):
    """Load the entire lattice from the data directory."""
    lattice = pytac.load_csv.load(ring_mode, mock.MagicMock())
    return lattice


def test_load_lattice_using_default_dir():
    lat = pytac.load_csv.load("VMX", mock.MagicMock())
    assert len(lat) == 2142


@pytest.mark.parametrize(
    "lattice, name, n_elements, length",
    [
        (lazy_fixture("vmx_ring"), "VMX", 2142, 561.571),
        (lazy_fixture("diad_ring"), "DIAD", 2144, 561.571),
    ],
)
def test_load_lattice(lattice, name, n_elements, length):
    assert len(lattice) == n_elements
    assert lattice.name == name
    assert (lattice.get_length() - length) < EPS


@pytest.mark.parametrize(
    "lattice, n_bpms",
    [(lazy_fixture("vmx_ring"), 173), (lazy_fixture("diad_ring"), 173)],
)
def test_get_pv_names(lattice, n_bpms):
    bpm_x_pvs = lattice.get_element_pv_names("BPM", "x", handle="readback")
    assert len(bpm_x_pvs) == n_bpms
    for pv in bpm_x_pvs:
        assert re.match("SR.*BPM.*X", pv)
    x_sofb_enabled_pvs = lattice.get_element_pv_names(
        "BPM", "x_sofb_disabled", handle="readback"
    )
    assert len(bpm_x_pvs) == n_bpms
    for pv in x_sofb_enabled_pvs:
        assert re.match("SR.*HBPM.*SLOW:DISABLED", pv)


@pytest.mark.parametrize(
    "lattice, n_bpms",
    [(lazy_fixture("vmx_ring"), 173), (lazy_fixture("diad_ring"), 173)],
)
def test_load_bpms(lattice, n_bpms):
    bpms = lattice.get_elements("BPM")
    bpm_fields = {
        "x",
        "y",
        "enabled",
        "x_fofb_disabled",
        "x_sofb_disabled",
        "y_fofb_disabled",
        "y_sofb_disabled",
    }
    for bpm in bpms:
        assert set(bpm.get_fields()[pytac.LIVE]) == bpm_fields
        assert re.match("SR.*BPM.*X", bpm.get_pv_name("x", pytac.RB))
        with pytest.raises(pytac.exceptions.HandleException):
            bpm.get_pv_name("x", pytac.SP)
    assert len(bpms) == n_bpms
    assert bpms[0].cell == 1
    assert bpms[-1].cell == 24


@pytest.mark.parametrize(
    "lattice, n_drifts",
    [(lazy_fixture("vmx_ring"), 1308), (lazy_fixture("diad_ring"), 1311)],
)
def test_load_drift_elements(lattice, n_drifts):
    drifts = lattice.get_elements("DRIFT")
    assert len(drifts) == n_drifts


@pytest.mark.parametrize(
    "lattice, n_quads",
    [(lazy_fixture("vmx_ring"), 248), (lazy_fixture("diad_ring"), 248)],
)
def test_load_quadrupoles(lattice, n_quads):
    quads = lattice.get_elements("Quadrupole")
    assert len(quads) == n_quads
    for quad in quads:
        assert set(quad.get_fields()[pytac.LIVE]) == set(["b1"])
        device = quad.get_device("b1")
        assert re.match("SR.*Q.*:I", device.rb_pv)
        assert re.match("SR.*Q.*:SETI", device.sp_pv)


@pytest.mark.parametrize(
    "lattice, n_q1b, n_q1d",
    [(lazy_fixture("vmx_ring"), 34, 12), (lazy_fixture("diad_ring"), 34, 12)],
)
def test_load_quad_family(lattice, n_q1b, n_q1d):
    q1b = lattice.get_elements("Q1B")
    assert len(q1b) == n_q1b
    q1d = lattice.get_elements("Q1D")
    assert len(q1d) == n_q1d


@pytest.mark.parametrize(
    "lattice, n_correctors",
    [(lazy_fixture("vmx_ring"), 173), (lazy_fixture("diad_ring"), 172)],
)
def test_load_correctors(lattice, n_correctors):
    hcm = lattice.get_elements("HSTR")
    vcm = lattice.get_elements("VSTR")
    assert len(hcm) == n_correctors
    assert len(vcm) == n_correctors
    for element in hcm:
        # each one has x_kick, h_fofb_disabled and h_sofb_disabled fields.
        assert {"x_kick", "h_sofb_disabled", "h_fofb_disabled"}.issubset(
            element.get_fields()[pytac.LIVE]
        )
    for element in vcm:
        # each one has y_kick, v_fofb_disabled and v_sofb_disabled fields.
        assert {"y_kick", "v_sofb_disabled", "v_fofb_disabled"}.issubset(
            element.get_fields()[pytac.LIVE]
        )


@pytest.mark.parametrize(
    "lattice, n_squads",
    [(lazy_fixture("vmx_ring"), 98), (lazy_fixture("diad_ring"), 98)],
)
def test_load_squads(lattice, n_squads):
    squads = lattice.get_elements("SQUAD")
    assert len(squads) == n_squads
    for squad in squads:
        assert "a1" in squad.get_fields()[pytac.LIVE]
        device = squad.get_device("a1")
        assert re.match("SR.*SQ.*:I", device.rb_pv)
        assert re.match("SR.*SQ.*:SETI", device.sp_pv)


@pytest.mark.parametrize(
    "lattice", (lazy_fixture("diad_ring"), lazy_fixture("vmx_ring"))
)
def test_cell(lattice):
    # there are squads in every cell
    sq = lattice.get_elements("SQUAD")
    assert sq[0].cell == 1
    assert sq[-1].cell == 24


@pytest.mark.parametrize(
    "lattice", (lazy_fixture("diad_ring"), lazy_fixture("vmx_ring"))
)
@pytest.mark.parametrize("field", ("x", "y"))
def test_bpm_unitconv(lattice, field):
    bpm = lattice.get_elements("BPM")[0]
    uc = bpm._data_source_manager._uc[field]

    assert uc.eng_to_phys(1) == 0.001
    assert uc.phys_to_eng(2) == 2000


def test_hstr_unitconv(vmx_ring):
    # From MML: hw2physics('HTRIM', 'Monitor', 2.5, [1])
    htrim = vmx_ring.get_elements("HTRIM")[0]
    # This test depends on the lattice having an energy of 3000Mev.
    uc = htrim._data_source_manager._uc["x_kick"]
    numpy.testing.assert_allclose(uc.eng_to_phys(2.5), 0.0001925)
    numpy.testing.assert_allclose(uc.phys_to_eng(0.0001925), 2.5)


def test_quad_unitconv(vmx_ring):
    # From MML: hw2physics('Q1D', 'Monitor', 70, [1])
    q1d = vmx_ring.get_elements("Q1D")
    # This test depends on the lattice having an energy of 3000Mev.
    for q in q1d:
        uc = q._data_source_manager._uc["b1"]
        numpy.testing.assert_allclose(uc.eng_to_phys(70), -0.691334652255027)
        numpy.testing.assert_allclose(uc.phys_to_eng(-0.691334652255027), 70)


def test_quad_unitconv_raise_exception():
    uc = pytac.units.PchipUnitConv([50.0, 100.0, 180.0], [-4.95, -9.85, -17.56])
    with pytest.raises(pytac.exceptions.UnitsException):
        uc.phys_to_eng(-0.7)


def test_quad_unitconv_known_failing_test():
    LAT_ENERGY = 3000

    uc = pytac.units.PchipUnitConv([50.0, 100.0, 180.0], [-4.95, -9.85, -17.56])
    uc._post_eng_to_phys = pytac.utils.get_div_rigidity(LAT_ENERGY)
    uc._pre_phys_to_eng = pytac.utils.get_mult_rigidity(LAT_ENERGY)
    numpy.testing.assert_allclose(uc.eng_to_phys(70), -0.69133465)
    numpy.testing.assert_allclose(uc.phys_to_eng(-0.7), 70.8834284954)


@pytest.mark.parametrize("quad_index,phys_value", [[747, -1.9457], [1135, -1.9864]])
def test_quad_unitconv_with_different_limits(diad_ring, quad_index, phys_value):
    """Test elements with unit conversions that have different limits.

    The limits on these quads are different to the rest of the family.
    They caused problems until we implemented different limits per UnitConv
    object.
    """
    problem_quad = diad_ring[quad_index - 1]
    uc = problem_quad.get_unitconv("b1")
    # This is just outside the power supply limits 0 to 200A.
    uc.phys_to_eng(phys_value)
