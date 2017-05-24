from pytac import utils
import numpy


def test_rigidity():
    numpy.testing.assert_allclose(utils.rigidity(3000), 10.0069227)
