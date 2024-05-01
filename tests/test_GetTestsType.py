import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTestsType import GetTestsType
import pandas as pd 

# successful call
def test_GetTestsType_success():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for tests by type
    response = GetTestsType(typeId = "Countermovement Jump", from_=1690859091, to_=1695688065)
    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)