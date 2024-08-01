import pytest
from hdforce.AuthManager import AuthManager
from hdforce.GetTests import GetTests
import pandas as pd 

#----- Base Call -----#
# successful call with file
def test_GetTests_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")
    # Call for tests by type
    response = GetTests(from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)

#----- Athlete ID -----#
# successful call with file
def test_GetTests_Ath_file():
    
    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")
    # Call for tests by athlete
    response = GetTests(athleteId = "OLbsebtmf81eiwg1AeE5", from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)

#----- Group ID -----#
# successful call with file
def test_GetTests_Group_file():

    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")
    # Call for tests by group
    response = GetTests(groupId = "yh8RnOvg56dQNrZGBKWZ", from_= 1690859091, to_= 1700000000)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)

#----- Team ID -----#
# successful call with file
def test_GetTests_Team_file():

    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")
    # Call for tests by team
    response = GetTests(teamId = "vW9iEKafhs2PamfKSdGC", from_= 1690859091, to_= 1700000000)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)

#----- Test Type ID -----#
# successful call with file
def test_GetTests_Type_file():

    # Authenticate
    AuthManager(authMethod= "file", env_file_name= "tests\.env")
    # Call for tests by type
    response = GetTests(typeId = "Countermovement Jump", from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)

#--------------------------------------------------#

#----- Base Call -----#
# successful call with env
def test_GetTests_env():
    
    # Authenticate
    AuthManager()
    # Call for tests by type
    response = GetTests(from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)

#----- Athlete ID -----#
# successful call with env
def test_GetTests_Ath_env():
    
    # Authenticate
    AuthManager()
    # Call for tests by athlete
    response = GetTests(athleteId = "OLbsebtmf81eiwg1AeE5", from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)

#----- Group ID -----#
# successful call with env
def test_GetTests_Group_env():

    # Authenticate
    AuthManager()
    # Call for tests by group
    response = GetTests(groupId = "yh8RnOvg56dQNrZGBKWZ", from_= 1690859091, to_= 1700000000)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)


#----- Team ID -----#
# successful call with env
def test_GetTests_Team_env():

    # Authenticate
    AuthManager()
    # Call for tests by team
    response = GetTests(teamId = "vW9iEKafhs2PamfKSdGC", from_= 1690859091, to_= 1700000000)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)


#----- Test Type ID -----#
# successful call with env
def test_GetTests_Type_env():

    # Authenticate
    AuthManager()
    # Call for tests by type
    response = GetTests(typeId = "Countermovement Jump", from_=1690859091, to_=1695688065)

    # Check response is DataFrame
    assert isinstance(response, pd.DataFrame)
    assert isinstance(response.attrs['Count'], int)
    assert isinstance(response.attrs['Last Sync'], int)
    assert isinstance(response.attrs['Last Test Time'], int)