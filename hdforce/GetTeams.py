# Dependencies -----
import requests
import pandas as pd
from pandas import json_normalize

#--------------------#
## Get Teams -----
def GetTeams(token) -> pd.DataFrame:
    """Fetches and returns team names and IDs from an API, using an authentication token managed by a TokenManager instance.
    This function is designed to retrieve all teams within your organization.

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must
        have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the teams' information, with columns:
        - id: Team's unique identifier.
        - names: Team's given name.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request,
        or if there is a failure in parsing the JSON response.
    """

   # Retrieve Access Token and check expiration
    a_token = token.get_token()

    # API Cloud URL
    url_cloud = token.url_cloud

    # Create URL for request
    url = f"{url_cloud}/teams"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    # Response Handling
    # If Error show error
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.reason}")
    # If successful
    try:
        # Flatten test data from response
        data = response.json()
        df = json_normalize(data['data'], meta=['count'], errors='ignore')  # 
        return df
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")
