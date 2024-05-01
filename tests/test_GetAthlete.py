import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetAthletes import GetAthletes
import pandas as pd 
import os

# successful call
def test_GetAthletes_success():

    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")

    # Call for athletes
    players = GetAthletes()
    # Check response is DataFrame
    assert isinstance(players, pd.DataFrame)