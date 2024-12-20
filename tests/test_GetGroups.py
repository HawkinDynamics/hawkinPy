import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetGroups import GetGroups
import pandas as pd 

# successful call with file
def test_GetGroups_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= r"tests/.env")
    # Call for groups
    groups = GetGroups()
    
    # Check response is DataFrame
    assert isinstance(groups, pd.DataFrame)
    assert isinstance(groups.attrs['Count'], int)


# successful call with env
def test_GetGroups_env():
    
    # Authenticate
    AuthManager()
    # Call for groups
    groups = GetGroups()

    # Check response is DataFrame
    assert isinstance(groups, pd.DataFrame)
    assert isinstance(groups.attrs['Count'], int)