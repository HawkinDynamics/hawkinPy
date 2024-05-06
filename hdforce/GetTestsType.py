# Create function to call tests by type
import requests
import os
import datetime
import pandas as pd
# Package imports
from .utils import responseHandler, logger, ConfigManager
from .AuthManager import AuthManager

# -------------------- #
# Tests by Type


def GetTestsType(typeId: str, from_: int = None, to_: int = None, sync: bool = False, active: bool = True) -> pd.DataFrame:
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

    active : bool, optional
        If True, only active tests are fetched. If False, all tests including inactive ones are fetched. Default is True.

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
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug(f"Access Token retrieved. expires {datetime.datetime.fromtimestamp(tokenExp)}")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)
    if nowtime < tokenExp:
        logger.debug(f"Access Token valid through: {datetime.datetime.fromtimestamp(tokenExp)}")

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
        logger.debug(f"New Access Token valid through: {datetime.datetime.fromtimestamp(tokenExp)}")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # From DateTime
    from_dt = ""
    if from_ is not None:
        if sync:
            from_dt = f"&syncFrom={from_}"
        else:
            from_dt = f"&from={from_}"

    # To DateTime
    to_dt = ""
    if to_ is not None:
        if sync:
            to_dt = f"&syncTo={to_}"
        else:
            to_dt = f"&to={to_}"

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

    # Create URL for request
    url = f"{url_cloud}?testTypeId={t_id}{from_dt}{to_dt}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)
    # Log request
    if from_dt is not None and to_dt is not None:
        logger.debug(f"Test Type Request from_dt to_dt")
    elif from_dt is None:
        logger.debug(f"Test Type Request to_dt")
    elif to_dt is None:
        logger.debug(f"Test Type Request from_dt")

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
        if 'active' in df.columns and active:
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
