import types

import numpy

from pytac import utils


def test_rigidity():
    numpy.testing.assert_almost_equal(utils.get_rigidity(3.e+9),
                                      10006922.85594456)


def test_get_div_rigidity():
    div = utils.get_div_rigidity(3.e+9)
    assert isinstance(div, types.FunctionType)
    numpy.testing.assert_almost_equal(div(numpy.pi), 3.139419278848089e-07)
    numpy.testing.assert_almost_equal(div(1.e+8), 9.993081933333334)


def test_get_mult_rigidity():
    mult = utils.get_mult_rigidity(3.e+9)
    assert isinstance(mult, types.FunctionType)
    numpy.testing.assert_almost_equal(mult(numpy.pi), 31437675.329275224)
    numpy.testing.assert_almost_equal(mult(1.e-8), 0.10006922855944561)
