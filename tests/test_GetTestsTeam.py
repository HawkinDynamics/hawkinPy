import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTestsTeam import GetTestsTeam
import pandas as pd 

# successful call
def test_GetTestsTeam_success():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for tests by team
    response = GetTestsTeam(teamId = "vW9iEKafhs2PamfKSdGC", from_= 1690859091, to_= 1700000000)
    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)