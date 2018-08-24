import mock
import pytest
import pytac


@pytest.fixture(scope="session")
def vmx_ring():
    return pytac.load_csv.load('VMX', mock.MagicMock)


@pytest.fixture(scope="session")
def diad_ring():
    return pytac.load_csv.load('DIAD', mock.MagicMock)
