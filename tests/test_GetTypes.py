import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTypes import GetTypes
import pandas as pd 

# successful call with file
def test_GetTypes_file():

    # Authenticate
    AuthManager(authMethod= "file", env_file_name= r"tests/.env")
    # Call for test types
    data = GetTypes()

    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)


# successful call with env
def test_GetTypes_env():

    # Authenticate
    AuthManager()
    # Call for metrics
    data = GetTypes()

    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
