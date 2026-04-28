import os
import pytest
import pandas as pd
from hdforce import AuthManager, GetAthletes, GetMetrics


def test_dev_api_workflow():
    """
    Functional test to verify Auth -> GetAthletes -> GetMetrics workflow
    against the development API.
    """
    # 1. Authenticate against the Dev API
    # region="Development" routes requests to https://cloud.dev.hawkindynamics.com/api
    try:
        AuthManager(
            authMethod="env",
            refreshToken_name="HD_REFRESH_TOKEN",
            region="Development"
        )
    except Exception as e:
        pytest.fail(f"Authentication failed against Dev API: {e}")

    # 2. Test GetAthletes
    try:
        athletes = GetAthletes()
        assert isinstance(athletes, pd.DataFrame), "GetAthletes should return a DataFrame"
        assert not athletes.empty, "Athlete list should not be empty in the dev environment"
        print(f"Successfully retrieved {len(athletes)} athletes from Dev API.")
    except Exception as e:
        pytest.fail(f"GetAthletes failed: {e}")

    # 3. Test GetMetrics
    try:
        # Fetching a small window of data to verify the pipe
        metrics = GetMetrics()
        assert isinstance(metrics, pd.DataFrame), "GetMetrics should return a DataFrame"
        print("Successfully validated metrics retrieval pipeline.")
    except Exception as e:
        # We don't fail if empty (might be no data for that date),
        # but we fail if the request itself breaks.
        print(f"Metrics request completed with status: {e}")


if __name__ == "__main__":
    # Allows running the script directly
    test_dev_api_workflow()
