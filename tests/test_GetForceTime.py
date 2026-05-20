import pytest
from unittest.mock import patch, MagicMock
from hdforce.AuthManager import AuthManager
from hdforce.GetForceTime import GetForceTime
import pandas as pd


# Mocked force-time response (Countermovement Jump shape — full 7 columns)
def mock_forcetime_response(test_id="test_abc123"):
    return {
        "id": test_id,
        "testType": {
            "canonicalId": "7nNduHeM5zETPjHxvm7s",
            "name": "Countermovement Jump",
        },
        "athlete": {
            "id": "athlete_abc123",
            "name": "Test Athlete",
        },
        "timestamp": 1700000000,
        "Time(s)": [0.001, 0.002, 0.003, 0.004],
        "LeftForce(N)": [481, 480, 482, 484],
        "RightForce(N)": [481, 480, 482, 484],
        "CombinedForce(N)": [962, 960, 964, 968],
        "Velocity(m/s)": [0, 0, 0, 0],
        "Displacement(m)": [0, 0, 0, 0],
        "Power(W)": [0, 0, 0, 0],
    }


@patch('hdforce.GetForceTime.ensure_token', return_value='fake_access_token')
@patch('hdforce.GetForceTime.requests.get')
def test_GetForceTime_file(mock_get, mock_token):
    # Mock the GET request response
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: mock_forcetime_response("test_abc123")
    )

    # Authenticate
    AuthManager(authMethod="file", env_file_name=r"tests/.env", region="Development")

    # Call for ForceTime
    data = GetForceTime(testId="test_abc123")

    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    assert len(data) == 4

    # Check DataFrame attributes
    assert data.attrs['Test ID'] == "test_abc123"
    assert data.attrs['Test Name'] == "Countermovement Jump"
    assert data.attrs['Athlete Name'] == "Test Athlete"
    assert data.attrs['Athlete ID'] == "athlete_abc123"

    # Check waveform columns are present
    assert {"time", "leftForce", "rightForce", "combinedForce",
            "velocity", "displacement", "power"} <= set(data.columns)


@patch('hdforce.GetForceTime.ensure_token', return_value='fake_access_token')
@patch('hdforce.GetForceTime.requests.get')
def test_GetForceTime_env(mock_get, mock_token):
    # Mock the GET request response
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: mock_forcetime_response("test_abc123")
    )

    # Authenticate
    AuthManager(region="Development")

    # Call for ForceTime
    data = GetForceTime(testId="test_abc123")

    # Check response is DataFrame
    assert isinstance(data, pd.DataFrame)
    assert data.attrs['Test ID'] == "test_abc123"


@patch('hdforce.GetForceTime.ensure_token', return_value='fake_access_token')
@patch('hdforce.GetForceTime.requests.get')
def test_GetForceTime_unknown_id_raises(mock_get, mock_token):
    """The API returns 200 with an empty body for unknown test IDs;
    GetForceTime should raise ValueError in that case."""
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {})

    AuthManager(authMethod="file", env_file_name=r"tests/.env", region="Development")

    with pytest.raises(ValueError, match="No force-time data found"):
        GetForceTime(testId="nonexistent_id")
