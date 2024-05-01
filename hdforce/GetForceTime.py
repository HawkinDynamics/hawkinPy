# Dependencies -----
import requests
import pandas as pd
import os
import datetime
# Package imports
from .LogConfig import LoggerConfig
from .utils import logger, ConfigManager
from .AuthManager import AuthManager

#--------------------#
## Get Force Time
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
    logger.debug("::GetForceTime:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetForceTime:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetForceTime:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetForceTime:: ACCESS_TOKEN expired.")
        # autheniticate
        try:
            AuthManager(
                region= ConfigManager.region,
                authMethod= ConfigManager.env_method,
                refreshToken_name= ConfigManager.token_name,
                refreshToken= ConfigManager.refresh_token,
                env_file_name= ConfigManager.file_name
            )
            # Retrieve Access Token and check expiration
            a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
            logger.debug("::GetForceTime - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetForceTime - Validat:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetForceTime - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetForceTime - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetForceTime - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetForceTime - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetForceTime:: ACCESS_TOKEN retrieved and valid.")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # Test ID
    if isinstance(testId, str):
        tid = testId
    else:
        logger.error("::GetForceTime:: TestId must be a string")
        raise ValueError("Error: TestId must be a string")

    # Create URL for request
    url = f"{url_cloud}/forcetime/{tid}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)
    logger.debug("::GetForceTime:: GET request sent for force-time data.")

    # Check response status and handle data accordingly
    if response.status_code != 200:
        logger.error(f"::GetForceTime:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    try:
        # Flatten test data from response
        data = response.json()
        # Create DataFrame from the array data
        df = pd.DataFrame({
            "Time(s)": data["Time(s)"],
            "LeftForce(N)": data["LeftForce(N)"],
            "RightForce(N)": data["RightForce(N)"],
            "CombinedForce(N)": data["CombinedForce(N)"],
            "Velocity(m/s)": data["Velocity(m/s)"],
            "Displacement(m)": data["Displacement(m)"],
            "Power(W)": data["Power(W)"],
            "rsi": [data["rsi"]] * len(data["Time(s)"])  # Assuming rsi is a constant value
        })
        
        # Setting attributes
        df.attrs['Test ID'] = data['id']
        df.attrs['Test Name'] = data['testType']['name']
        df.attrs['Athlete Name'] = data['athlete']['name']
        df.attrs['Athlete ID'] = data['athlete']['id']
        df.attrs['Timestamp'] = pd.to_datetime(data['timestamp'], unit='s')
        df.attrs['RSI'] = data['rsi']
        logger.info(f"::GetForceTime:: Request for {df.attrs['Test Name']} ::{df.attrs['Test ID']}:: on {df.attrs['Timestamp']} successful.")  
        return df
    
    except ValueError:
        logger.error("::GetForceTime:: Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")
    