# Create function to call tests by Athlete
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
# Tests by Athlete

@deprecated('Use `GetTests` instead, which has been expanded to handle all requests.')
def GetTestsAth(athleteId: str, from_: int = None, to_: int = None, sync: bool = False, includeInactive: bool = False) -> pd.DataFrame:
    """Get test trials for a specified athlete from an API. The function allows filtering of results based on time frames and the state of the test (active or not).

    Parameters
    ----------
    athleteId : str
        The unique identifier of the athlete whose tests are to be retrieved.

    from_ : int, optional
        Unix timestamp specifying the start time from which tests should be fetched. Default is None, which fetches tests from the beginning.

    to_ : int, optional
        Unix timestamp specifying the end time until which tests should be fetched. Default is None, which fetches tests up to the current time.

    sync : bool, optional
        If True, the function fetches updated and newly created tests to synchronize with the Hawkin database. Default is False.

    includeInactive : bool, optional
        If False, only active tests are fetched. If True, all tests including inactive ones are fetched. Default is False.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing test trials matching the query criteria, with the following DataFrame attributes:
        - Athlete Id
        - Athlete Name
        - Last Sync Time
        - Last Test Time
        - Count of Tests

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    ValueError
        If the 'athleteId' parameter is not a string.
    
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

    # Create URL for request
    url = os.getenv("CLOUD_URL")

    # Create blank Query list to handle parameters
    query = {}

    # Athlete ID
    if isinstance(athleteId, str):
        query['athleteId'] = athleteId
    else:
        logger.error("athleteId incorrect. Check your entry")
        raise Exception("athleteId incorrect. Check your entry")

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
        logger.debug(f"Athlete Test Request from_dt to_dt")
    elif from_ is None:
        logger.debug(f"Athlete Test Request to_dt")
    elif to_ is None:
        logger.debug(f"Athlete Test Request from_dt")

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

        # Athlete Real Name
        aName = df['athlete_name'].unique()
        aName = str(aName[0])

        # Setting attributes
        df.attrs['Athlete Id'] = athleteId
        df.attrs['Athlete Name'] = aName
        df.attrs['Last Sync'] = int(data['lastSyncTime'])
        df.attrs['Last Test Time'] = int(data['lastTestTime'])
        df.attrs['Count'] = int(data['count'])
        logger.info(f"Request successful. Returned {df.attrs['Count']} tests from athlete: {athleteId}.")
        return df

    except requests.RequestException as e:
        return f"Request Error: {e}"

    except ValueError as e:
        return f"JSON Error: {e}"

    except Exception as e:
        return f"An error occurred: {e}"
