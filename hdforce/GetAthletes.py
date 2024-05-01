# Dependencies -----
import requests
import os
import datetime
import pandas as pd
# Package imports
from .LogConfig import LoggerConfig
from .utils import logger, ConfigManager
from .AuthManager import AuthManager

def GetAthletes(inactive: bool = False) -> pd.DataFrame:
    """Get the athlete information from an account.

    Parameters
    ----------
    inactive : bool, optional
        A boolean that specifies whether to include inactive athletes in the results. Default is False, meaning by default inactive athletes are not included.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the athletes' information, with columns:
        - id: Athlete's unique identifier.
        - names: Athlete's given full name.
        - teams: A nested list of athlete's team ids as strings.
        - groups: A nested list of athlete's group ids as strings.
        - active: Boolean indicating if the athlete's profile is active (not archived).
        - external: Columns dynamically created for each external attribute associated with the athletes. (example = external.ExternalId: value)

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    logger.debug("::GetAthletes:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetAthletes:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetAthletes:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetAthletes:: ACCESS_TOKEN expired.")
        # authenticate
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
            logger.debug("::GetAthletes - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetAthletes - Validate:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetAthletes - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetAthletes - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetAthletes - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetAthletes - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetAthletes:: ACCESS_TOKEN retrieved and valid.")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # Create URL for request
    url = f"{url_cloud}/athletes?inactive={inactive}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Create Response
    response = requests.get(url, headers=headers)
    if inactive:
        logger.debug("::GetAthletes:: GET request sent for ALL athletes (+ inactive).")
    else:
        logger.debug("::GetAthletes:: GET request sent for ACTIVE athletes.")
    
    # Response Handling
    # If Error show error
    if response.status_code != 200:
        logger.error(f"::GetAthletes:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")
    # If successful
    try:
        data = response.json()['data']
        df = pd.json_normalize(data, meta=['count'], errors='ignore')
        count = str(len(df.index))
        # Setting attributes
        logger.info(f"::GetAthletes:: Request successful. Athletes returned: {count}")
        return df
    # Bad parse or none returned
    except ValueError:
        logger.error("::GetAthletes:: Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")
