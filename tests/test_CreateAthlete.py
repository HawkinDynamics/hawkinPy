import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from hdforce.AuthManager import AuthManager
from hdforce.CreateAthletes import CreateAthletes
from hdforce.Classes import NewAthlete, AthleteResult

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
        'failures': [{
            'reason': 'Duplicate or Invalid Athlete Name',
            'data': {'name': f'Name_{formatted_time}'}
        }]
    }

# Successful call with file


@patch('hdforce.CreateAthletes.requests.post')
def test_CreateAthletes_file(mock_post):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the POST request response
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: mock_success_response(formatted_time))

    # Authenticate
    AuthManager(authMethod="file", env_file_name=r"tests/.env", region="Development")

    # Create New Athletes
    players = [
        NewAthlete(name=f"Name_{formatted_time}", active=False)
    ]

    # Create Athlete
    response = CreateAthletes(athletes=players)

    # Response is a list of AthleteResult objects (one per input athlete)
    assert isinstance(response, list)
    assert len(response) == 1
    assert all(isinstance(r, AthleteResult) for r in response)

    # Single successful result
    result = response[0]
    assert result.successful is True
    assert result.name == f"Name_{formatted_time}"
    assert result.id == 'athlete_id_1'
    assert result.reason == []

# Successful call with env


@patch('hdforce.CreateAthletes.requests.post')
def test_CreateAthletes_env(mock_post):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the POST request response
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: mock_success_response(formatted_time))

    # Authenticate
    AuthManager(region="Development")

    # Create New Athletes
    players = [
        NewAthlete(name=f"Name_{formatted_time}", active=False)
    ]

    # Create Athlete
    response = CreateAthletes(athletes=players)

    # Response is a list of AthleteResult objects (one per input athlete)
    assert isinstance(response, list)
    assert len(response) == 1
    assert all(isinstance(r, AthleteResult) for r in response)

    # Single successful result
    result = response[0]
    assert result.successful is True
    assert result.name == f"Name_{formatted_time}"
    assert result.id == 'athlete_id_1'
    assert result.reason == []

# Test for failure response


@patch('hdforce.CreateAthletes.requests.post')
def test_CreateAthletes_failure(mock_post):
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # Mock the POST request response
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: mock_failure_response(formatted_time))

    # Authenticate
    AuthManager(authMethod="file", env_file_name=r"tests/.env", region="Development")

    # Create New Athletes
    players = [
        NewAthlete(name=f"Name_{formatted_time}", active=False)
    ]

    # Create Athlete
    response = CreateAthletes(athletes=players)

    # Response is a list of AthleteResult objects (one per input athlete)
    assert isinstance(response, list)
    assert len(response) == 1
    assert all(isinstance(r, AthleteResult) for r in response)

    # Single failed result
    result = response[0]
    assert result.successful is False
    assert result.name == f"Name_{formatted_time}"
    assert result.id == ''
    assert 'Duplicate or Invalid Athlete Name' in result.reason
