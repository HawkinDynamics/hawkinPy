# Create function to call tests by type
import requests
import pandas as pd
from .utils import responseHandler

#--------------------#
## Tests by Athlete
def GetTestsAth(token, athleteId: str, from_: int = None, to_: int = None, sync: bool = False, active: bool = True) -> pd.DataFrame:
    """Fetches and returns test trials for a specified athlete from an API, using an authentication token managed by a TokenManager instance.
    The function allows filtering of results based on time frames and the state of the test (active or not).

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must
        have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

    athleteId : str
        The unique identifier of the athlete whose tests are to be retrieved.

    from_ : int, optional
        Unix timestamp specifying the start time from which tests should be fetched. Default is None, which fetches tests from the beginning.

    to_ : int, optional
        Unix timestamp specifying the end time until which tests should be fetched. Default is None, which fetches tests up to the current time.

    sync : bool, optional
        If True, the function fetches updated and newly created tests to synchronize with the Hawkin database. Default is False.

    active : bool, optional
        If True, only active tests are fetched. If False, all tests including inactive ones are fetched. Default is True.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing test trials matching the query criteria, with the following DataFrame attirbutes:
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
    """
    # Retrieve Access Token and Expiration from .env file
    a_token = token.get_token()

    # API Cloud URL
    url_cloud = token.url_cloud  # Make sure this is a property or method that exists

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

    # Athlete ID
    if isinstance(athleteId, str):
        a_id = athleteId
    else:
        raise Exception("athleteId incorrect. Check your entry")
        

    # Create URL for request
    url = f"{url_cloud}?athleteId={a_id}{from_dt}{to_dt}"

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

        # Athlete Real Name
        aName = df['athlete.name'].unique()

        # Setting attributes
        df.attrs['Athlete Id'] = a_id
        df.attrs['Athlete Name'] = aName[0]
        df.attrs['Last Sync'] = data['lastSyncTime']
        df.attrs['Last Test Time'] = data['lastTestTime']
        df.attrs['Count'] = data['count']

        return df
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")