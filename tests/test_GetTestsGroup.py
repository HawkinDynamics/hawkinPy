import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTestsGroup import GetTestsGroup
import pandas as pd 

# successful call
def test_GetTestsGroup_success():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for tests by group
    response = GetTestsGroup(groupId = "yh8RnOvg56dQNrZGBKWZ", from_= 1690859091, to_= 1700000000)
    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)