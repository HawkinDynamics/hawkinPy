# Dependencies -----
from .utils import logger, ConfigManager
from .AuthManager import AuthManager
import requests
import os
import datetime
import pandas as pd

def GetMetrics() -> pd.DataFrame:
    """
    Fetches and returns test metrics from an API, using an authentication token managed by a TokenManager instance.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the test metrics, with columns:
        - id: The unique identifier for each metric.
        - name: The name of each metric.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    logger.debug("::GetMetrics:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetMetrics:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetMetrics:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetMetrics:: ACCESS_TOKEN expired.")
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
            logger.debug("::GetMetrics - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetMetrics - Validat:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetMetrics - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetMetrics - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetMetrics - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetMetrics - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetMetrics:: ACCESS_TOKEN retrieved and valid.")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # Create URL for request
    url = f"{url_cloud}/metrics"  # Note: Removed the underscore from "/test_Types" to "/test_types"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Create Response
    response = requests.get(url, headers=headers)
    logger.debug("::GetMetrics:: GET request sent for Metrics.")

    # Response Handling
    # If Error show error
    if response.status_code != 200:
        logger.error(f"::GetMetrics:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")
    # If successful
    try:
        # Flatten test data from response
        data = response.json()
        # Create DataFrame from JSON
        df = pd.DataFrame(data)
        # Explode 'metrics' column to expand each list element into a row
        df = df.explode('metrics')
        # Normalize 'metrics' column
        metrics_df = pd.json_normalize(df['metrics'])
        # Concatenate the original DataFrame with the normalized metrics DataFrame
        result_df = pd.concat([df.drop('metrics', axis=1).reset_index(drop=True), metrics_df], axis=1)
        logger.info(f"::GetMetrics:: Request for Metrics successful") 
        return(result_df)
    
    except ValueError:
        logger.error("::GetMetrics:: Failed to parse JSON response or no data returned")
        raise Exception("Failed to parse JSON response or no data returned.")