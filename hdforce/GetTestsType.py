# Create function to call tests by type
import requests
import pandas as pd
from .utils import responseHandler
#--------------------#
## Tests by Type
def GetTestsType(token, typeId: str, from_: int = None, to_: int = None, sync: bool = False, active: bool = True) -> pd.DataFrame:
    """Fetches and returns test trials based on a specific test type from an API, using an authentication token managed by a TokenManager instance.
    Allows filtering of results based on time frames and the state of the test (active or not).

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must
        have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

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
        raise Exception("typeId incorrect. Check your entry")

    # Create URL for request
    url = f"{url_cloud}?testTypeId={t_id}{from_dt}{to_dt}"

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
        
        # Create Test Type info for df attrs
        if t_id in type_ids:
            type_info = type_ids[t_id]

        # Setting attributes
        df.attrs['Cannonical Id'] = type_info[0]
        df.attrs['Test Type Name'] = type_info[1]
        df.attrs['Last Sync'] = data['lastSyncTime']
        df.attrs['Last Test Time'] = data['lastTestTime']
        df.attrs['Count'] = data['count']

        return df
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")
