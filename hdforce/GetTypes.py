# Dependencies -----
from .utils import logger, ConfigManager
from .AuthManager import AuthManager
import requests
import os
import datetime
import pandas as pd

def GetTypes() -> pd.DataFrame:
    """Fetches and returns the test type names and IDs from an API.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the test types, with columns:
        - id: The unique identifier for each test type.
        - name: The name of each test type.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request,
        or if there is a failure in parsing the JSON response.
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    logger.debug("::GetTypes:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetTypes:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetTypes:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetTypes:: ACCESS_TOKEN expired.")
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
            logger.debug("::GetTypes - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetTypes - Validat:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetTypes - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetTypes - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetTypes - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetTypes - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetTypes:: ACCESS_TOKEN retrieved and valid.")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # Construct the API endpoint URL
    url = f"{url_cloud}/test_types"

    # Setup the authorization headers for the API request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Send the GET request to the API
    response = requests.get(url, headers=headers)
    logger.debug("::GetTypes:: GET request sent for Test Types.")

    # Check if the API response was successful
    if response.status_code != 200:
        logger.error(f"::GetTypes:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    # Try to parse the JSON data returned by the API
    try:
        data = response.json()
        df = pd.DataFrame.from_records(data)
        count = str(len(df.index))
        logger.info(f"::GetTypes:: Request successful. Types returned: {count}")
        return df
    
    except ValueError:
        logger.error("::GetTypes:: Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")
