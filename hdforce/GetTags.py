# Dependencies -----
import requests
import os
import datetime
import pandas as pd
# Package imports
from .LogConfig import LoggerConfig
from .utils import logger, ConfigManager
from .AuthManager import AuthManager

#--------------------#
## Get Tags -----
def GetTags() -> pd.DataFrame:
    """Get tag names, IDs, and descriptions for an account. This function is designed to retrieve all tags within the system.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the tags' information, with columns:
        - id: Tag's unique identifier.
        - name: Tag's given name.
        - desc: Description of the tag.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request,
        or if there is a failure in parsing the JSON response.
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    logger.debug("::GetTags:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetTags:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetTags:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetTags:: ACCESS_TOKEN expired.")
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
            logger.debug("::GetTags - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetTags - Validat:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetTags - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetTags - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetTags - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetTags - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetTags:: ACCESS_TOKEN retrieved and valid.")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # Create URL for request
    url = f"{url_cloud}/tags"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)
    logger.debug("::GetTags:: GET request sent for Tags")

    # Response Handling
    # If Error show error
    if response.status_code != 200:
        logger.error(f"::GetTags:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")
    # If successful
    try:
        # Flatten test data from response
        data = response.json()
        df = pd.json_normalize(data['data'], meta=['count'], errors='ignore') 
        count = str(len(df.index))
        logger.info(f"::GetTags:: Request successful. Tags returned: {count}")  
        return df
    except ValueError:
        logger.error("::GetTags:: Failed to parse JSON response or no data returned")
        raise Exception("Failed to parse JSON response or no data returned.")
    