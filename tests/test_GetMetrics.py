import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetMetrics import GetMetrics
import pandas as pd 

# successful call
def test_GetMetrics_success():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for metrics
    metrics = GetMetrics()
    # Check response is DataFrame
    assert isinstance(metrics, pd.DataFrame)