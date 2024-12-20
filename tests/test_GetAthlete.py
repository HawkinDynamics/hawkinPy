import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetAthletes import GetAthletes
import pandas as pd 
import os

# successful call with file
def test_GetAthletes_file():

    # Authenticate
    AuthManager(authMethod= "file", env_file_name= r"tests/.env")
    # Call for athletes
    players = GetAthletes()

    # Check response is DataFrame
    assert isinstance(players, pd.DataFrame)
    assert isinstance(players.attrs["Count"], int)

# successful call with env
def test_GetAthletes_env():

    # Authenticate
    AuthManager()
    # Call for athletes
    players = GetAthletes()

    # Check response is DataFrame
    assert isinstance(players, pd.DataFrame)
    assert isinstance(players.attrs["Count"], int)