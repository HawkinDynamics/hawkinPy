import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetGroups import GetGroups
import pandas as pd 

# successful call
def test_GetGroups_success():
    
    # Authenticate
    AuthManager(authMethod = 'file', env_file_name = '.env')

    # Call for groups
    groups = GetGroups()
    # Check response is DataFrame
    assert isinstance(groups, pd.DataFrame)