import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from hdforce.AuthManager import AuthManager
from hdforce.UpdateAthletes import UpdateAthletes
from hdforce.Classes import Athlete, AthleteResult

# Mocked response generator for successful athlete update
def mock_success_response(formatted_time):
    return {
        'data': [{'name': f'Name_{formatted_time}', 'id': 'athlete_id_1'}],
        'failures': []
    }

# Mocked response generator for failed athlete update
def mock_failure_response(formatted_time):
    return {
        'data': [],
        'failures': [{'reason': 'Duplicate or Invalid Athlete Name', 'data': {'name': f'Name_{formatted_time}', 'id': 'athlete_id_1'}}]
    }

# Successful call with file
@patch('hdforce.UpdateAthletes.requests.put')
def test_UpdateAthletes_file(mock_put):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the PUT request response
    mock_put.return_value = MagicMock(status_code=200, json=lambda: mock_success_response(formatted_time))

    # Authenticate
    AuthManager(authMethod="file", env_file_name="tests/.env")

    # Create New Athletes
    players = [
        Athlete(id="athlete_id_1", name=f"Name_{formatted_time}", active=True)
    ]

    # Update Athlete
    response = UpdateAthletes(athletes=players)

    # Check response is a list of AthleteResult
    assert isinstance(response, list)
    assert all(isinstance(result, AthleteResult) for result in response)

    # Check successful athletes
    assert len(response) == 1
    assert response[0].name == f"Name_{formatted_time}"
    assert response[0].successful is True
    assert response[0].id == "athlete_id_1"
    assert response[0].reason == []

# Successful call with env
@patch('hdforce.UpdateAthletes.requests.put')
def test_UpdateAthletes_env(mock_put):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the PUT request response
    mock_put.return_value = MagicMock(status_code=200, json=lambda: mock_success_response(formatted_time))

    # Authenticate
    AuthManager()

    # Create New Athletes
    players = [
        Athlete(id="athlete_id_1", name=f"Name_{formatted_time}", active=True)
    ]

    # Update Athlete
    response = UpdateAthletes(athletes=players)

    # Check response is a list of AthleteResult
    assert isinstance(response, list)
    assert all(isinstance(result, AthleteResult) for result in response)

    # Check successful athletes
    assert len(response) == 1
    assert response[0].name == f"Name_{formatted_time}"
    assert response[0].successful is True
    assert response[0].id == "athlete_id_1"
    assert response[0].reason == []

# Test for failure response
@patch('hdforce.UpdateAthletes.requests.put')
def test_UpdateAthletes_failure(mock_put):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the PUT request response
    mock_put.return_value = MagicMock(status_code=200, json=lambda: mock_failure_response(formatted_time))

    # Authenticate
    AuthManager(authMethod="file", env_file_name="tests/.env")

    # Create New Athletes
    players = [
        Athlete(id="athlete_id_1", name=f"Name_{formatted_time}", active=True)
    ]

    # Update Athlete
    response = UpdateAthletes(athletes=players)

    # Check response is a list of AthleteResult
    assert isinstance(response, list)
    assert all(isinstance(result, AthleteResult) for result in response)

    # Check failures
    assert len(response) == 1
    assert response[0].name == f"Name_{formatted_time}"
    assert response[0].successful is False
    assert response[0].id == "athlete_id_1"
    assert response[0].reason == ['Duplicate or Invalid Athlete Name']