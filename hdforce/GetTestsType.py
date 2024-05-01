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
## Tests by Type
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
        A DataFrame containing test trials matching the query criteria, with appropriate columns depending on the test data and the following DataFrame attirbutes:
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
    logger.debug("::GetTestsType:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetTestsType:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetTestsType:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetTestsType:: ACCESS_TOKEN expired.")
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
            logger.debug("::GetTestsType - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetTestsType - Validat:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetTestsType - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetTestsType - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetTestsType - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetTestsType - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetTestsType:: ACCESS_TOKEN retrieved and valid.")

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
        "2uS5XD5kXmWgIZ5HhQ3A": [ "2uS5XD5kXmWgIZ5HhQ3A", "Isometric Test", "ISO"],
        "gyBETpRXpdr63Ab2E0V8": [ "gyBETpRXpdr63Ab2E0V8", "Drop Jump", "DJ"],
        "5pRSUQVSJVnxijpPMck3": [ "5pRSUQVSJVnxijpPMck3", "Free Run", "FREE"],
        "pqgf2TPUOQOQs6r0HQWb": [ "pqgf2TPUOQOQs6r0HQWb", "CMJ Rebound", "CMJR"],
        "r4fhrkPdYlLxYQxEeM78": [ "r4fhrkPdYlLxYQxEeM78", "Multi Rebound", "MR"],
        "ubeWMPN1lJFbuQbAM97s": [ "ubeWMPN1lJFbuQbAM97s", "Weigh In", "WI"],
        "rKgI4y3ItTAzUekTUpvR": [ "rKgI4y3ItTAzUekTUpvR", "Drop Landing", "DL"]
    }

    for key, values in type_ids.items():
        if typeId in values:
            t_id = key
            break
    else:
        logger.error("::GetTestsType:: typeId incorrect. Check your entry")
        raise Exception("typeId incorrect. Check your entry")

    # Create URL for request
    url = f"{url_cloud}?testTypeId={t_id}{from_dt}{to_dt}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)
    logger.debug(f"::GetTestsType:: GET request sent for Tests by test type: {t_id}.")

    # Check response status and handle data accordingly
    if response.status_code != 200:
        logger.error(f"::GetTestsType:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    try:
        data = response.json()
        # run data handler function
        df = responseHandler(data)

        # Filter active tests if required
        if 'active' in df.columns and active:
            df = df[df['active'] == True]
        
        # Create Test Type info for df attrs
        if t_id in type_ids:
            type_info = type_ids[t_id]

        # Setting attributes
        df.attrs['Cannonical Id'] = type_info[0]
        df.attrs['Test Type Name'] = type_info[1]
        df.attrs['Last Sync'] = data['lastSyncTime']
        df.attrs['Last Test Time'] = data['lastTestTime']
        df.attrs['Count'] = data['count']
        logger.info(f"::GetTestsType:: Request successful. Returned {df.attrs['Count']} {df.attrs['Test Type Name']} tests.")  
        return df
    
    except ValueError:
        logger.error("::GetTestsType:: Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")
