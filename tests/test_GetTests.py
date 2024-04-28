import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTests import GetTests
import pandas as pd 

# successful call
def test_GetTests_success():
    
    # Authenticate
    AuthManager(authMethod = 'file', env_file_name = '.env')

    # Call for tests by type
    response = GetTests(from_time=1700000000, to_time=1710000000)
    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)