import pytac
import pytest
import os
import re
import mock
import numpy
from pytac.exceptions import UniqueSolutionException


EPS = 1e-8


@pytest.fixture
def lattice():
    basepath = os.getcwd()
    filename = os.path.join(basepath, 'data/')
    lattice = pytac.load_csv.load('VMX', mock.MagicMock(), filename)
    return lattice


def test_load_lattice(lattice):
    assert len(lattice) == 2131
    assert lattice.name == 'VMX'
    assert (lattice.get_length() - 561.571) < EPS


def test_get_family_pvs(lattice):
    bpm_x_pvs = lattice.get_family_pvs('BPM', 'x', handle='readback')
    assert len(bpm_x_pvs) == 173
    for pv in bpm_x_pvs:
        assert re.match('SR.*BPM.*X', pv)


def test_load_bpms(lattice):
    bpms = lattice.get_elements('BPM')
    for bpm in bpms:
        assert set(bpm._devices.keys()) == set(('x', 'y'))
    assert len(bpms) == 173


def test_load_drift_elements(lattice):
    drifts = lattice.get_elements('DRIFT')
    assert len(drifts) == 1308


def test_load_quadrupoles(lattice):
    quads = lattice.get_elements('QUAD')
    assert len(quads) == 248
    for quad in quads:
        assert set(quad._devices.keys()) == set(('b1',))
        device = quad.get_device('b1')
        assert re.match('SR.*Q.*:I', device.rb_pv)
        assert re.match('SR.*Q.*:SETI', device.sp_pv)


def test_load_quad_family(lattice):
    q1b = lattice.get_elements('Q1B')
    assert len(q1b) == 34
    q1b = lattice.get_elements('Q1D')
    assert len(q1b) == 12


def test_load_correctors(lattice):
    hcm = lattice.get_elements('HSTR')
    vcm = lattice.get_elements('VSTR')
    assert len(hcm) == 173
    assert len(vcm) == 173

@pytest.mark.parametrize('field', ('x', 'y'))
def test_bpm_unitconv(lattice, field):
    bpm = lattice.get_elements('BPM')[0]
    uc = bpm._uc[field]
    print('p is {}'.format(uc.p))

    assert uc.eng_to_phys(1) == 0.001
    assert uc.phys_to_eng(2) == 2000


def test_load_lattice_using_default_dir():
    lat = pytac.load_csv.load('VMX', mock.MagicMock())
    assert len(lat) == 2131


def test_quad_unitconv(lattice):
    q1d = lattice.get_elements('Q1D')
    lattice._energy = 3000
    for q in q1d:
        uc = q._uc['b1']
        numpy.testing.assert_allclose(uc.eng_to_phys(70), -6.918132432432433)
        numpy.testing.assert_allclose(uc.phys_to_eng(-6.918132432432433), 70)


def test_quad_unitconv_raise_exception(lattice):
    LAT_ENERGY = 3000

    element = pytac.element.Element('raise_exception', 10, 'q1d')
    uc = pytac.units.PchipUnitConv([50.0, 100.0, 180.0], [-4.95, -9.85, -17.56])
    with pytest.raises(UniqueSolutionException):
        numpy.testing.assert_allclose(uc.phys_to_eng(-0.7), 70.8834284954)


def test_quad_unitconv_known_failing_test(lattice):
    LAT_ENERGY = 3000

    element = pytac.element.Element('failing_element', 10, 'q1d')
    uc = pytac.units.PchipUnitConv([50.0, 100.0, 180.0], [-4.95, -9.85, -17.56])
    uc._post_eng_to_phys = pytac.load_csv.get_div_rigidity(LAT_ENERGY)
    uc._pre_phys_to_eng = pytac.load_csv.get_mult_rigidity(LAT_ENERGY)
    numpy.testing.assert_allclose(uc.eng_to_phys(70), -0.69133465)
    numpy.testing.assert_allclose(uc.phys_to_eng(-0.7),  70.8834284954)
