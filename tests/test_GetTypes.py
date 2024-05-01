import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTypes import GetTypes
import pandas as pd 

# successful call
def test_GetTypes_success():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for test types
    types = GetTypes()
    # Check response is DataFrame
    assert isinstance(types, pd.DataFrame)