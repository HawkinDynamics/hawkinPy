import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetForceTime import GetForceTime
import pandas as pd 

# successful call
def test_GetForceTime_success():
    
    # Authenticate
    AuthManager(authMethod = 'file', env_file_name = '.env')

    # Call for ForceTime
    ftdata = GetForceTime(testId = "9Ytz9g1erMXm3SByTyEd")
    # Check response is DataFrame
    assert isinstance(ftdata, pd.DataFrame)