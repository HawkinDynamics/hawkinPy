# Dependencies -----
import requests
import os
import datetime
import pandas as pd
# Package imports
from .utils import responseHandler, logger, ConfigManager, deprecated
from .AuthManager import AuthManager
# Enable deprecation warnings globally
import warnings
warnings.simplefilter('always', DeprecationWarning)
# -------------------- #
# Tests by Team

@deprecated('Use `GetTests` instead, which has been expanded to handle all requests.')
def GetTestsTeam(teamId: str, from_: int = None, to_: int = None, sync: bool = False, includeInactive: bool = False) -> pd.DataFrame:
    """Get test trials for specified team(s). Allows filtering of results based on time frames, synchronization needs, and the active status of tests.

    Parameters
    ----------
    teamId : str
        A single team ID, tuple or list of team IDs to receive tests from specific teams.

    from_ : int, optional
        Unix timestamp specifying the start time from which tests should be fetched. Default is None, which fetches tests from the beginning.

    to_ : int, optional
        Unix timestamp specifying the end time until which tests should be fetched. Default is None, which fetches tests up to the current time.

    sync : bool, optional
        If True, the function fetches updated and newly created tests to synchronize with the database. Default is False.

    includeInactive : bool, optional
        Default to False, where only active tests are returned. If True, all tests including inactive ones are returned.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing test trials matching the query criteria, with columns dependent on the test data and the following DataFrame attributes:
        - Team IDs
        - Last Sync Time
        - Last Test Time
        - Count of Tests

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    ValueError
        If the 'teamId' parameter is not properly formatted as a string or a list/tuple of strings.
    
    Deprecated
    ----------
    Use `GetTests` instead, which has been expanded to handle all requests.
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
    url = os.getenv("CLOUD_URL")

    # Create blank Query list to handle parameters
    query = {}

    # Handling teamId input whether single ID or tuple of IDs
    if isinstance(teamId, (tuple, list)):
        query['teamId']  = ','.join(map(str, teamId))  # Join multiple team IDs into a comma-separated string
    elif isinstance(teamId, str):
        query['teamId'] = teamId  # Use the single team ID as is
    else:
        logger.error("teamId must be a string or a tuple/list of strings.")
        raise ValueError("teamId must be a string or a tuple/list of strings.")

    # Evaluate from and to dates for Sync command
    if sync is True:
        if from_ is not None:
            query['syncFrom'] = from_
        if to_ is not None:
            query['syncTo'] = to_
    elif sync is False:
        if from_ is not None:
            query['from'] = from_
        if to_ is not None:
            query['to'] = to_

    # Log request
    if from_ is not None and to_ is not None:
        logger.debug(f"Team Test Request from_dt to_dt")
    elif from_ is None:
        logger.debug(f"Team Test Request to_dt")
    elif to_ is None:
        logger.debug(f"Team Test Request from_dt")
    
    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers, params=query)

    # Check response status and handle data accordingly
    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    try:
        data = response.json()
        # Check if the data dictionary is empty
        if data.get('count', 0) == 0:
            logger.info("No tests returned from query")
            return "No tests returned from query"

        # run data handler function
        df = responseHandler(data)

        # Filter active tests if required
        if 'active' in df.columns and includeInactive == False:
            df = df[df['active'] == True]

        # Setting attributes
        df.attrs['Team Id'] = teamId
        df.attrs['Last Sync'] = int(data['lastSyncTime'])
        df.attrs['Last Test Time'] = int(data['lastTestTime'])
        df.attrs['Count'] = int(data['count'])
        logger.info(f"Request successful. Returned {df.attrs['Count']} tests from Teams: {teamId}.")
        return df

    except requests.RequestException as e:
        return f"Request Error: {e}"

    except ValueError as e:
        return f"JSON Error: {e}"

    except Exception as e:
        return f"An error occurred: {e}"
