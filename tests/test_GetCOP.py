import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetCOP import GetCOP
import pandas as pd

# COP data is exclusive to the "Free Run" test type. This testId points at
# a known Free Run test with COP data on the dev API (a non–Free Run id
# would return 404).
COP_TEST_ID = "RnhZnPJi1iMEu3Ys27M4"

# successful call


def test_GetCOP_file():

    # Authenticate
    AuthManager(authMethod="file", env_file_name=r"tests/.env")

    # Call for COP
    data = GetCOP(testId=COP_TEST_ID)
    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    # Check attribute matches the requested id
    assert data.attrs['Test ID'] == COP_TEST_ID
    # COP columns are present
    assert "copX" in data.columns
    assert "leftCopX" in data.columns


# successful call
def test_GetCOP_env():

    # Authenticate
    AuthManager()
    # Call for COP
    data = GetCOP(testId=COP_TEST_ID)

    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    # Check attribute matches the requested id
    assert data.attrs['Test ID'] == COP_TEST_ID
