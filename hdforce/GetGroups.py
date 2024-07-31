# Dependencies -----
import requests
import os
import datetime
import pandas as pd
# Package imports
from .utils import logger, ConfigManager
from .AuthManager import AuthManager

# -------------------- #
# Get Groups -----


def GetGroups() -> pd.DataFrame:
    """Get group for an account. This function is designed to retrieve all groups within your organization.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the groups' information, with columns:
        - id: Group's unique identifier.
        - name: Group's name.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
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

    # Create URL for request
    url = f"{url_cloud}/groups"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Create Response
    logger.debug("GET Request: Groups")
    response = requests.get(url, headers=headers)

    # Response Handling
    # If Error show error
    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    # If successful
    try:
        # Flatten test data from response
        data = response.json()
        df = pd.json_normalize(data['data'], meta=['count'], errors='ignore')

        df.attrs['Count'] = int(len(df.index))
        count = str(len(df.index))
        logger.info(f"Request successful. Groups returned: {count}")
        return df

    except ValueError:
        logger.error("Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")
