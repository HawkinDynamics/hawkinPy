# Create function to call tests by type
import requests
import os
import datetime
import pandas as pd
# Package imports
from .LogConfig import LoggerConfig
from .utils import responseHandler, logger, ConfigManager
from .AuthManager import AuthManager

#--------------------#
## Get All Tests
def GetTests(from_=None, to_=None, sync=False, active=True) -> pd.DataFrame:
    """Get all test trials from an account. Allows filtering of results based on time frames, synchronization needs, and the active status of tests.

    Parameters
    ----------
    from_ : int, optional
        Unix timestamp specifying the start time from which tests should be fetched. Default is None, which fetches tests from the beginning.
    
    to_ : int, optional
        Unix timestamp specifying the end time until which tests should be fetched. Default is None, which fetches tests up to the current time.
    
    sync : bool, optional
        If True, the function fetches updated and newly created tests to synchronize with the database. Default is False.
    
    active : bool, optional
        If True, only active tests are fetched. If False, all tests including inactive ones are fetched. Default is True.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing test trials matching the query criteria, with columns dependent on the test data and the following DataFrame attirbutes:
        - Last Sync Time
        - Last Test Time
        - Count of Tests

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    ValueError
        If there is an error in handling the JSON response or data formatting.
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    logger.debug("::GetTests:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetTests:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetTests:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetTests:: ACCESS_TOKEN expired.")
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
            logger.debug("::GetTests - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetTests - Validat:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetTests - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetTests - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetTests - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetTests - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetTests:: ACCESS_TOKEN retrieved and valid.")
    
    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # From DateTime
    from_dt = ""
    if from_ is not None:
        if sync:
            from_dt = f"?syncFrom={from_}"
        else:
            from_dt = f"?from={from_}"

    # To DateTime
    to_dt = ""
    if to_ is not None:
        if from_ is None:
            to_dt = f"?{'syncTo' if sync else 'to'}={to_}"
        else:
            to_dt = f"&{'syncTo' if sync else 'to'}={to_}"

    # Create URL for request
    url = f"{url_cloud}{from_dt}{to_dt}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)
    logger.debug("::GetTests:: GET request sent for Tests.")

    # Check response status and handle data accordingly
    if response.status_code != 200:
        logger.error(f"::GetTests:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    try:
        data = response.json()
        # run data handler function
        df = responseHandler(data)

        # Filter active tests if required
        if 'active' in df.columns and active:
            df = df[df['active'] == True]
        
        # Setting attributes
        df.attrs['Last Sync'] = data['lastSyncTime']
        df.attrs['Last Test Time'] = data['lastTestTime']
        df.attrs['Count'] = data['count']
        logger.info(f"::GetTests:: Request successful. Tests returned: {data['count']}")
        return df
    
    except ValueError:
        logger.error("::GetTests:: Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")
