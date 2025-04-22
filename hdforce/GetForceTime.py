# Dependencies -----
import requests
import pandas as pd
import os
import datetime
# Package imports
from .utils import logger, ConfigManager
from .AuthManager import AuthManager

# -------------------- #
# Get Force Time


def GetForceTime(testId: str) -> pd.DataFrame:
    """Get force-time data for an individual test trial from an account.

    Parameters
    ----------
    testId : str
        The unique ID given to each test trial.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing details of the test trial, with columns:
        - Time (s): Time elapsed in seconds.
        - LeftForce (N): Force at time point from left plate.
        - RightForce (N): Force at time point from right plate.
        - CombinedForce (N): Combined force (Left + Right) at each time point.
        - Velocity (m/s): Calculated center of mass velocity at each time point.
        - Displacement (m): Calculated center of mass displacement from starting height at each time point.
        - Power (W): Calculated power of mass at each time point.
        - RSI: Calculated Reactive Strength Index (if applicable).

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request,
        or if there is a failure in parsing the JSON response.
    ValueError
        If the 'testId' parameter is not a string.
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("No Access Token found.")
        raise Exception("No Access Token found.")
    elif int(nowtime) >= tokenExp:
        logger.debug(f"Token Expired: {datetime.datetime.fromtimestamp(tokenExp)}")
        # authenticate
        try:
            AuthManager(
                region=ConfigManager.region,
                authMethod=ConfigManager.env_method,
                refreshToken_name=ConfigManager.token_name,
                refreshToken=ConfigManager.refresh_token,
                env_file_name=ConfigManager.file_name
            )
            # Retrieve Access Token and check expiration
            a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
            logger.debug("New ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("No Access Token found.")
                raise Exception("No Access Token found.")
            elif int(nowtime) >= tokenExp:
                logger.debug(f"Token Expired: {datetime.datetime.fromtimestamp(tokenExp)}")
                raise Exception("Token expired")
            else:
                logger.debug(f"New Access Token valid through: {datetime.datetime.fromtimestamp(tokenExp)}")
                pass
        except ValueError:
            logger.error("Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage")
    else:
        logger.debug(f"Access Token retrieved. expires {datetime.datetime.fromtimestamp(tokenExp)}")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # Test ID
    if isinstance(testId, str):
        tid = testId
    else:
        logger.error("TestId must be a string")
        raise Exception("Error: TestId must be a string")

    # Create URL for request
    url = f"{url_cloud}/forcetime/{tid}"

    # GET Request
    logger.debug(f"GET Force-Time data for test: {tid}")
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    # Check response status and handle data accordingly
    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    try:
        # Flatten test data from response
        data = response.json()

        # Get Test Type
        test_type = data['testType']['canonicalId']

        def pad_array(arr, target_length, pad_value=None):
            return arr + [pad_value] * (target_length - len(arr))

        # Target length is the length of the primary time array
        target_length = len(data.get("Time(s)", []))

        time_data = data.get("Time(s)", [])
        left_force = pad_array(data.get("LeftForce(N)", []), target_length, None)
        right_force = pad_array(data.get("RightForce(N)", []), target_length, None)
        combined_force = pad_array(data.get("CombinedForce(N)", []), target_length, None)
        velocity = pad_array(data.get("Velocity(m/s)", []), target_length, None)
        displacement = pad_array(data.get("Displacement(m)", []), target_length, None)
        power = pad_array(data.get("Power(W)", []), target_length, None)

        # Create DataFrame from the array data
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
        elif test_type in ["4KlQgKmBxbOY6uKTLDFL", "umnEZPgi6zaxuw0KhUpM"]:  # TruStrength tests
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

        # Setting attributes
        df.attrs['Test ID'] = data['id']
        df.attrs['Test Name'] = data['testType']['name']
        df.attrs['Athlete Name'] = data['athlete']['name']
        df.attrs['Athlete ID'] = data['athlete']['id']
        df.attrs['Timestamp'] = pd.to_datetime(data['timestamp'], unit='s')
        logger.info(f"Request successful: {df.attrs['Test Name']} - {df.attrs['Test ID']} - {df.attrs['Timestamp']}")
        return df

    except ValueError:
        logger.error("Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")