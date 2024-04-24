# Create function to call tests by type
import requests
import pandas as pd
from .utils import responseHandler

#--------------------#    
## Tests by Team
def GetTestsTeam(token, teamId: str, from_: int = None, to_: int = None, sync: bool = False, active: bool = True) -> pd.DataFrame:
    """Fetches and returns test trials for specified team(s) from an API, using an authentication token managed by a TokenManager instance.
    Allows filtering of results based on time frames, synchronization needs, and the active status of tests.

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must
        have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

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
    # Retrieve Access Token and Expiration from .env file
    a_token = token.get_token()

    # API Cloud URL
    url_cloud = token.url_cloud  # Make sure this is a property or method that exists

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
        raise ValueError("teamId must be a string or a tuple/list of strings.")
        
    # Create URL for request
    url = f"{url_cloud}?teamId={t_id}{from_dt}{to_dt}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    # Check response status and handle data accordingly
    if response.status_code != 200:
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
            
        return df
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")
