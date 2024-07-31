# Dependencies -----
import requests
import os
import datetime
import pandas as pd
# Package imports
from .utils import logger, ConfigManager
from .AuthManager import AuthManager

# ----------------- #
# Get Metrics


def GetMetrics() -> pd.DataFrame:
    """
    Get the metrics and ids for all the metrics in the system

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the test metrics, with columns:
        - canonicalTestTypeId: The unique identifier for each test type.
        - testTypeName: The name of each metric.
        - id: The unique identifier for each metric.
        - label: The label (common name) for each metric
        - units: Units of measure
        - description: Full description of metric and calculation*

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
    url = f"{url_cloud}/metrics" 

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Create Response
    logger.debug("GET Request: Metrics.")
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
        # Create DataFrame from JSON
        df = pd.DataFrame(data)
        # Explode 'metrics' column to expand each list element into a row
        df = df.explode('metrics')
        # Normalize 'metrics' column
        metrics_df = pd.json_normalize(df['metrics'])
        # Concatenate the original DataFrame with the normalized metrics DataFrame
        result_df = pd.concat([df.drop('metrics', axis=1).reset_index(drop=True), metrics_df], axis=1)

        result_df.attrs['Count'] = int(len(result_df))
        logger.info("Request for Metrics successful")
        return result_df

    except ValueError:
        logger.error("Failed to parse JSON response or no data returned")
        raise Exception("Failed to parse JSON response or no data returned.")
