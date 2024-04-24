# Dependencies -----
import requests
import pandas as pd
from pandas import json_normalize

def GetAthletes(token, inactive=False) -> pd.DataFrame:
    """Fetches and returns athlete information from an API, using an authentication token managed by a TokenManager instance. Optionally includes inactive athletes based on the `inactive` parameter.

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.
    
    inactive : bool, optional
        A boolean that specifies whether to include inactive athletes in the results. Default is False, meaning by default inactive athletes are not included.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the athletes' information, with columns:
        - id: Athlete's unique identifier.
        - names: Athlete's given full name.
        - teams: Comma-separated string of athlete's teams.
        - groups: Comma-separated string of athlete's groups.
        - active: Boolean indicating if the athlete's profile is active (not archived).
        - external: Columns dynamically created for each external attribute associated with the athletes. (example = external.ExternalId: value)

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    """
    # Retrieve Access Token and check expiration
    a_token = token.get_token()

    # API Cloud URL
    url_cloud = token.url_cloud 

    # Create URL for request
    url = f"{url_cloud}/athletes?inactive={inactive}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Create Response
    response = requests.get(url, headers=headers)
    
    # Response Handling
    # If Error show error
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.reason}")
    # If successful
    try:
        data = response.json()['data']
        df = json_normalize(data, meta=['count'], errors='ignore')

        return df
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")
