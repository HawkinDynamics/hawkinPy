import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTestsAth import GetTestsAth
import pandas as pd 

# successful call with file
def test_GetTestsAth_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")
    # Call for tests by athlete
    response = GetTestsAth(athleteId = "OLbsebtmf81eiwg1AeE5", from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)


# successful call with env
def test_GetTestsAth_env():
    
    # Authenticate
    AuthManager()
    # Call for tests by athlete
    response = GetTestsAth(athleteId = "OLbsebtmf81eiwg1AeE5", from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)