import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTestsAth import GetTestsAth
import pandas as pd 

# successful call
def test_GetTestsAth_success():
    
    # Authenticate
    AuthManager(authMethod = 'file', env_file_name = '.env')

    # Call for tests by athlete
    response = GetTestsAth(athleteId = "OLbsebtmf81eiwg1AeE5")
    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)