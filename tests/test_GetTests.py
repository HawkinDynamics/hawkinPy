import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTests import GetTests
import pandas as pd 

# successful call
def test_GetTests_success():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for tests by type
    response = GetTests(from_=1690859091, to_=1695688065)
    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)