import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTags import GetTags
import pandas as pd 

# successful call
def test_GetTags_success():
    
    # Authenticate
    AuthManager(authMethod = 'file', env_file_name = '.env')

    # Call for tags
    tags = GetTags()
    # Check response is DataFrame
    assert isinstance(tags, pd.DataFrame)