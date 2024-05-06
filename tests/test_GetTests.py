import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTests import GetTests
import pandas as pd 

# successful call with file
def test_GetTests_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")
    # Call for tests by type
    response = GetTests(from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)


# successful call with env
def test_GetTests_env():
    
    # Authenticate
    AuthManager()
    # Call for tests by type
    response = GetTests(from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)
