# Create function to call tests by Teams
import requests
import os
import datetime
import pandas as pd
from .utils import responseHandler, logger, ConfigManager
from .AuthManager import AuthManager

#--------------------#    
## Tests by Team
def GetTestsTeam(teamId: str, from_: int = None, to_: int = None, sync: bool = False, active: bool = True) -> pd.DataFrame:
    """Fetches and returns test trials for specified team(s) from an API. Allows filtering of results based on time frames, synchronization needs, and the active status of tests.

    Parameters
    ----------
    teamId : str
        A single team ID or a comma-separated string of team IDs to receive tests from specific teams.

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
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    logger.debug("::GetTestsTeam:: ACCESS_TOKEN retrieved")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
    logger.debug("::GetTestsTeam:: TOKEN_EXPIRATION retrieved")

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("::GetTestsTeam:: No ACCESS_TOKEN found.")
        raise Exception(f"No Access Token found. Run authManager to gain access.")
    elif int(nowtime) >= tokenExp:
        logger.debug("::GetTestsTeam:: ACCESS_TOKEN expired.")
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
            logger.debug("::GetTestsTeam - Validate:: ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("::GetTestsTeam - Validat:: TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("::GetTestsTeam - Validate:: No ACCESS_TOKEN found.")
                raise Exception(f"No Access Token found. Run authManager to gain access.")
            elif int(nowtime) >= tokenExp:
                logger.error("::GetTestsTeam - Validate:: ACCESS_TOKEN expired.")
                raise Exception(f"Token expired. Run authManager to gain access.")
            else:
                logger.debug("::GetTestsTeam - Validate:: ACCESS_TOKEN retrieved and valid.")
                pass
        except ValueError:
            logger.error("::GetTestsTeam - Validate:: Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage") 
    else:
        logger.debug("::GetTestsTeam:: ACCESS_TOKEN retrieved and valid.")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # From datetime
    from_dt = f"&syncFrom={from_}" if from_ is not None and sync else f"&from={from_}" if from_ is not None else ""

    # To datetime
    to_dt = f"&syncTo={to_}" if to_ is not None and sync else f"&to={to_}" if to_ is not None else ""

    # Handling teamId input whether single ID or tuple of IDs
    if isinstance(teamId, (tuple, list)):
        t_id = ','.join(map(str, teamId))  # Join multiple team IDs into a comma-separated string
    elif isinstance(teamId, str):
        t_id = teamId  # Use the single team ID as is
    else:
        logger.error("::GetTestsTeam:: teamId must be a string or a tuple/list of strings.")
        raise ValueError("teamId must be a string or a tuple/list of strings.")
        
    # Create URL for request
    url = f"{url_cloud}?teamId={t_id}{from_dt}{to_dt}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)
    logger.debug(f"::GetTestsTeam:: GET request sent for Tests by Teams: {t_id}.")

    # Check response status and handle data accordingly
    if response.status_code != 200:
        logger.error(f"::GetTestsTeam:: Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")

    try:
        data = response.json()
        # run data handler function
        df = responseHandler(data)

        # Filter active tests if required
        if 'active' in df.columns and active:
            df = df[df['active'] == True]
        
        # Setting attributes
        df.attrs['Team Id'] = teamId
        df.attrs['Last Sync'] = data['lastSyncTime']
        df.attrs['Last Test Time'] = data['lastTestTime']
        df.attrs['Count'] = data['count']
        logger.info(f"::GetTestsTeam:: Request successful. Returned {df.attrs['Count']} tests from Teams: {teamId}.")
        return df
    
    except ValueError:
        logger.error("::GetTestsTeam:: Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")
