import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetMetrics import GetMetrics
import pandas as pd 

# successful call with file
def test_GetMetrics_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests/.env")
    # Call for metrics
    metrics = GetMetrics()
    
    # Check response is DataFrame
    assert isinstance(metrics, pd.DataFrame)
    assert isinstance(metrics.attrs['Count'], int)


# successful call with env
def test_GetMetrics_env():
    
    # Authenticate
    AuthManager()
    # Call for metrics
    metrics = GetMetrics()

    # Check response is DataFrame
    assert isinstance(metrics, pd.DataFrame)
    assert isinstance(metrics.attrs['Count'], int)