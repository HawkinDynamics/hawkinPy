import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTags import GetTags
import pandas as pd 

# successful call with file
def test_GetTags_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= r"tests/.env")
    # Call for metrics
    data = GetTags()
    
    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.attrs['Count'], int)


# successful call with env
def test_GetTags_env():
    
    # Authenticate
    AuthManager()
    # Call for metrics
    data = GetTags()

    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.attrs['Count'], int)