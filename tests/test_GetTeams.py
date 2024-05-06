import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTeams import GetTeams
import pandas as pd 

# successful call with file
def test_GetTeams_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests/.env")
    # Call for teams
    data = GetTeams()
    
    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.attrs['Count'], int)


# successful call with env
def test_GetTeams_env():
    
    # Authenticate
    AuthManager()
    # Call for teams
    data = GetTeams()

    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.attrs['Count'], int)