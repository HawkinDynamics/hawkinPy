import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from hdforce.AuthManager import AuthManager
from hdforce.CreateAthletes import CreateAthletes
from hdforce.Classes import NewAthlete
from typing import Optional
from pydantic import BaseModel

# Define AthleteResult Class in the test file
class AthleteResult(BaseModel):
    name: str
    successful: bool
    id: Optional[str] = None
    reason: Optional[str] = None

# Mocked response generator for successful athlete creation
def mock_success_response(formatted_time):
    return {
        'data': [{'name': f'Name_{formatted_time}', 'id': 'athlete_id_1'}],
        'failures': []
    }

# Mocked response generator for failed athlete creation
def mock_failure_response(formatted_time):
    return {
        'data': [],
        'failures': [{'reason': 'Duplicate or Invalid Athlete Name', 'data': {'name': f'Name_{formatted_time}'}}]
    }

# Successful call with file
@patch('hdforce.CreateAthletes.requests.post')
def test_CreateAthletes_file(mock_post):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the POST request response
    mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_success_response(formatted_time))

    # Authenticate
    AuthManager(authMethod="file", env_file_name="tests/.env")

    # Create New Athletes
    players = [
        NewAthlete(name=f"Name_{formatted_time}", active=False)
    ]

    # Create Athlete
    response = CreateAthletes(athletes=players)

    # Check response is a dictionary
    assert isinstance(response, dict)
    assert 'successful' in response
    assert 'failures' in response

    # Check successful athletes
    assert len(response['successful']) == 1
    assert response['successful'][0] == f"Name_{formatted_time}"

    # Check failures
    assert len(response['failures']) == 0

# Successful call with env
@patch('hdforce.CreateAthletes.requests.post')
def test_CreateAthletes_env(mock_post):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the POST request response
    mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_success_response(formatted_time))

    # Authenticate
    AuthManager()

    # Create New Athletes
    players = [
        NewAthlete(name=f"Name_{formatted_time}", active=False)
    ]

    # Create Athlete
    response = CreateAthletes(athletes=players)

    # Check response is a dictionary
    assert isinstance(response, dict)
    assert 'successful' in response
    assert 'failures' in response

    # Check successful athletes
    assert len(response['successful']) == 1
    assert response['successful'][0] == f"Name_{formatted_time}"

    # Check failures
    assert len(response['failures']) == 0

# Test for failure response
@patch('hdforce.CreateAthletes.requests.post')
def test_CreateAthletes_failure(mock_post):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the POST request response
    mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_failure_response(formatted_time))

    # Authenticate
    AuthManager(authMethod="file", env_file_name="tests/.env")

    # Create New Athletes
    players = [
        NewAthlete(name=f"Name_{formatted_time}", active=False)
    ]

    # Create Athlete
    response = CreateAthletes(athletes=players)

    # Check response is a dictionary
    assert isinstance(response, dict)
    assert 'successful' in response
    assert 'failures' in response

    # Check successful athletes
    assert len(response['successful']) == 0

    # Check failures
    assert len(response['failures']) == 1
    assert 'Duplicate or Invalid Athlete Name' in response['failures']
    assert response['failures']['Duplicate or Invalid Athlete Name'][0] == f"Name_{formatted_time}"

