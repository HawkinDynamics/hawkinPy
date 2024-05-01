import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetForceTime import GetForceTime
import pandas as pd 

# successful call
def test_GetForceTime_success():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for ForceTime
    data = GetForceTime(testId = "9Ytz9g1erMXm3SByTyEd")
    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)