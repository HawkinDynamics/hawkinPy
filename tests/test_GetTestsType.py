import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTestsType import GetTestsType
import pandas as pd 

# successful call
def test_GetTestsType_success():
    
    # Authenticate
    AuthManager(authMethod = 'file', env_file_name = '.env')

    # Call for tests by type
    response = GetTestsType(typeId = "Countermovement Jump")
    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)