# Create function to call tests by type
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
# Tests by Type

@deprecated('Use `GetTests` instead, which has been expanded to handle all requests.')
def GetTestsType(typeId: str, from_: int = None, to_: int = None, sync: bool = False, includeInactive: bool = False) -> pd.DataFrame:
    """Get tests trials based on a specific test type from an API. Allows filtering of results based on time frames and the state of the test (active or not).

    Parameters
    ----------
    typeId : str
        The canonical test ID, test type name, or test name abbreviation. Must correspond to known test types.

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
        A DataFrame containing test trials matching the query criteria, with appropriate columns depending on the test data and the following DataFrame attributes:
        - Canonical ID
        - ATest Type Name
        - Last Sync Time
        - Last Test Time
        - Count of Tests

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    Exception
        If the provided 'typeId' does not match any known test types, causing an inability to proceed with the API request.
    
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

    # Create blank Query list to handle parameters
    query = {}

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

    # Check typeId
    type_ids = {
        "7nNduHeM5zETPjHxvm7s": ["7nNduHeM5zETPjHxvm7s", "Countermovement Jump", "CMJ"],
        "QEG7m7DhYsD6BrcQ8pic": ["QEG7m7DhYsD6BrcQ8pic", "Squat Jump", "SJ"],
        "2uS5XD5kXmWgIZ5HhQ3A": ["2uS5XD5kXmWgIZ5HhQ3A", "Isometric Test", "ISO"],
        "gyBETpRXpdr63Ab2E0V8": ["gyBETpRXpdr63Ab2E0V8", "Drop Jump", "DJ"],
        "5pRSUQVSJVnxijpPMck3": ["5pRSUQVSJVnxijpPMck3", "Free Run", "FREE"],
        "pqgf2TPUOQOQs6r0HQWb": ["pqgf2TPUOQOQs6r0HQWb", "CMJ Rebound", "CMJR"],
        "r4fhrkPdYlLxYQxEeM78": ["r4fhrkPdYlLxYQxEeM78", "Multi Rebound", "MR"],
        "ubeWMPN1lJFbuQbAM97s": ["ubeWMPN1lJFbuQbAM97s", "Weigh In", "WI"],
        "rKgI4y3ItTAzUekTUpvR": ["rKgI4y3ItTAzUekTUpvR", "Drop Landing", "DL"]
    }

    for key, values in type_ids.items():
        if typeId in values:
            t_id = key
            break
    else:
        logger.error("typeId incorrect. Check your entry")
        raise Exception("typeId incorrect. Check your entry")

    # Add Test Type Id to params query
    query['testTypeId'] = t_id
    
    # Create URL for request
    url = os.getenv("CLOUD_URL")

    # Log request
    if from_ is not None and to_ is not None:
        logger.debug(f"Test Type Request from_dt to_dt")
    elif from_ is None:
        logger.debug(f"Test Type Request to_dt")
    elif to_ is None:
        logger.debug(f"Test Type Request from_dt")

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

        # Create Test Type info for df attrs
        if t_id in type_ids:
            type_info = type_ids[t_id]

        # Setting attributes
        df.attrs['Canonical Id'] = type_info[0]
        df.attrs['Test Type Name'] = type_info[1]
        df.attrs['Last Sync'] = int(data['lastSyncTime'])
        df.attrs['Last Test Time'] = int(data['lastTestTime'])
        df.attrs['Count'] = int(data['count'])
        logger.info(f"Request successful. Returned {df.attrs['Count']} {df.attrs['Test Type Name']} tests.")
        return df

    except requests.RequestException as e:
        return f"Request Error: {e}"

    except ValueError as e:
        return f"JSON Error: {e}"

    except Exception as e:
        return f"An error occurred: {e}"
