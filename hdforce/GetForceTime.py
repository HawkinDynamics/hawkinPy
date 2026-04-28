# Dependencies -----
import requests
import pandas as pd
import os
# Package imports
from .utils import logger, ensure_token

# -------------------- #
# Get Force Time


def GetForceTime(testId: str) -> pd.DataFrame:
    """Get force-time data for an individual test trial.

    Parameters
    ----------
    testId : str
        The unique ID of the test trial.

    Returns
    -------
    pd.DataFrame
        A DataFrame with force-time series columns (varies by test
        type). DataFrame attributes include Test ID, Test Name,
        Athlete Name, Athlete ID, and Timestamp.

    Raises
    ------
    Exception
        If the HTTP response status is not 200.
    ValueError
        If testId is not a string.
    """
    a_token = ensure_token()
    url_cloud = os.getenv("CLOUD_URL")

    if not isinstance(testId, str):
        logger.error("TestId must be a string")
        raise ValueError("TestId must be a string")

    url = f"{url_cloud}/forcetime/{testId}"

    logger.debug(f"GET Force-Time data for test: {testId}")
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(
            f"Error {response.status_code}: {response.reason}"
        )

    data = response.json()
    # The API returns 200 with an empty body for unknown test IDs.
    if not data or 'testType' not in data:
        logger.error(f"No force-time data found for testId: {testId}")
        raise ValueError(
            f"No force-time data found for testId '{testId}'. "
            f"The test may not exist or may not have force-time data."
        )
    test_type = data['testType']['canonicalId']

    def pad_array(arr, target_length, pad_value=None):
        return arr + [pad_value] * (target_length - len(arr))

    target_length = len(data.get("Time(s)", []))

    time_data = data.get("Time(s)", [])
    left_force = pad_array(
        data.get("LeftForce(N)", []), target_length, None
    )
    right_force = pad_array(
        data.get("RightForce(N)", []), target_length, None
    )
    combined_force = pad_array(
        data.get("CombinedForce(N)", []), target_length, None
    )
    velocity = pad_array(
        data.get("Velocity(m/s)", []), target_length, None
    )
    displacement = pad_array(
        data.get("Displacement(m)", []), target_length, None
    )
    power = pad_array(
        data.get("Power(W)", []), target_length, None
    )

    # Build DataFrame based on test type
    if test_type in [
        "r4fhrkPdYlLxYQxEeM78",  # Multi Rebound
        "2uS5XD5kXmWgIZ5HhQ3A",  # Isometric
        "5pRSUQVSJVnxijpPMck3",  # Free Run
        "ubeWMPN1lJFbuQbAM97s"   # Weigh In
    ]:
        df = pd.DataFrame({
            "time": time_data,
            "leftForce": left_force,
            "rightForce": right_force,
            "combinedForce": combined_force
        })
    elif test_type in [
        "4KlQgKmBxbOY6uKTLDFL",  # TS Free Run
        "umnEZPgi6zaxuw0KhUpM"   # TS Isometric
    ]:
        df = pd.DataFrame({
            "time": time_data,
            "combinedForce": combined_force
        })
    else:
        df = pd.DataFrame({
            "time": time_data,
            "leftForce": left_force,
            "rightForce": right_force,
            "combinedForce": combined_force,
            "velocity": velocity,
            "displacement": displacement,
            "power": power
        })

    # Set attributes
    df.attrs['Test ID'] = data['id']
    df.attrs['Test Name'] = data['testType']['name']
    df.attrs['Athlete Name'] = data['athlete']['name']
    df.attrs['Athlete ID'] = data['athlete']['id']
    df.attrs['Timestamp'] = pd.to_datetime(
        data['timestamp'], unit='s'
    )

    logger.info(
        f"Request successful: {df.attrs['Test Name']} - "
        f"{df.attrs['Test ID']} - {df.attrs['Timestamp']}"
    )
    return df
