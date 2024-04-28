import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTeams import GetTeams
import pandas as pd 

# successful call
def test_GetTeams_success():
    
    # Authenticate
    AuthManager(authMethod = 'file', env_file_name = '.env')

    # Call for teams
    teams = GetTeams()
    # Check response is DataFrame
    assert isinstance(teams, pd.DataFrame)