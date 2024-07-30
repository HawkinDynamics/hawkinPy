# Create function to call tests by type
import requests
import os
import datetime
import pandas as pd
# Package imports
from .utils import responseHandler, logger, ConfigManager
from .AuthManager import AuthManager

# -------------------- #
# Get All Tests


def GetTests(from_=None, to_=None, sync=False, athleteId=None, typeId=None, teamId=None, groupId=None, includeInactive = False) -> pd.DataFrame:
    """Get all test trials from an account. Allows filtering of results based on time frames, synchronization needs, and the active status of tests.

    Parameters
    ----------
    from_ : int, optional
        Unix timestamp specifying the start time from which tests should be fetched. Default is None, which fetches tests from the beginning.

    to_ : int, optional
        Unix timestamp specifying the end time until which tests should be fetched. Default is None, which fetches tests up to the current time.

    sync : bool, optional
        If True, the function fetches updated and newly created tests to synchronize with the database. Default is False.

    athleteId : str optional
        The unique identifier of the athlete whose tests are to be retrieved.

    typeId : str optional
        The canonical test ID, test type name, or test name abbreviation. Must correspond to known test types.

    teamId : str optional
        A single team ID, tuple or list of team IDs to receive tests from specific teams.

    groupId : str optional
        A single group ID or a comma-separated string of group IDs to receive tests from specific groups.

    includeInactive : bool, optional
        Default to False, where only active tests are returned. If True, all tests including inactive ones are returned.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing test trials matching the query criteria, with columns dependent on the test data and the following DataFrame attributes:
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

    # Check if more than one of the specified parameters is provided
    provided_params = [athleteId, typeId, teamId, groupId]
    provided_count = sum(1 for param in provided_params if param is not None)
    # Error if more than one key parameter provided
    if provided_count > 1:
        raise ValueError("Only one of athleteId, typeId, teamId, or groupId can be provided at the same time.")

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

    # Evaluate for Athlete argument
    if athleteId is not None:
        query['athleteId'] = athleteId

    # Evaluate for Test Type argument
    if typeId is not None:
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
        # Sort test type Id
        for key, values in type_ids.items():
            if typeId in values:
                t_id = key
                break
        else:
            logger.error("typeId incorrect. Check your entry")
            raise Exception("typeId incorrect. Check your entry")

        # Add Test Type Id to params query
        query['testTypeId'] = t_id

    # Evaluate for Team Id argument
    if teamId is not None:
        # Handling teamId input whether single ID or tuple of IDs
        if isinstance(teamId, (tuple, list)):
            query['teamId']  = ','.join(map(str, teamId))  # Join multiple team IDs into a comma-separated string
        elif isinstance(teamId, str):
            query['teamId'] = teamId  # Use the single team ID as is
        else:
            logger.error("teamId must be a string or a tuple/list of strings.")
            raise ValueError("teamId must be a string or a tuple/list of strings.")


    # Evaluate for Group Id argument
    if groupId is not None:
        # Handling groupId input whether single ID or tuple of IDs
        if isinstance(groupId, (tuple, list)):
            query['groupId']  = ','.join(map(str, groupId))  # Join multiple team IDs into a comma-separated string
        elif isinstance(groupId, str):
            query['groupId'] = groupId  # Use the single team ID as is
        else:
            logger.error("groupId must be a string or a tuple/list of strings.")
            raise ValueError("groupId must be a string or a tuple/list of strings.")

    # Log request
    if from_ is not None and to_ is not None:
        logger.debug(f"Test Request from_dt to_dt")
    elif from_ is None:
        logger.debug(f"Test Request to_dt")
    elif to_ is None:
        logger.debug(f"Test Request from_dt")
    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers, params=query)

    # Check response status and handle data accordingly
    if response.status_code != 200:
        logger.error(f"{response.status_code}: {response.reason}")
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
        # Create Test Type info for df attrs
        if typeId:
            if t_id in type_ids:
                type_info = type_ids[t_id]

        # Create team info for df attrs
        if teamId:
            df.attrs['Team Id'] = teamId

        # Create group info for df attrs
        if groupId:
            df.attrs['Group Id'] = groupId

        # Athlete Real Name
        if athleteId:
            aName = df['athlete_name'].unique()
            aName = str(aName[0])
            df.attrs['Athlete Id'] = athleteId
            df.attrs['Athlete Name'] = aName
        
        df.attrs['Last Sync'] = int(data['lastSyncTime'])
        df.attrs['Last Test Time'] = int(data['lastTestTime'])
        df.attrs['Count'] = int(data['count'])
        logger.info(f"Request successful. Tests returned: {data['count']}")
        return df

    except requests.RequestException as e:
        return f"Request Error: {e}"

    except ValueError as e:
        return f"JSON Error: {e}"

    except Exception as e:
        return f"An error occurred: {e}"
