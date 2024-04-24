# Dependencies -----
import requests
import pandas as pd
from pandas import json_normalize

#--------------------#
## Get Tags -----
def GetTags(token) -> pd.DataFrame:
    """Fetches and returns tag names, IDs, and descriptions from an API, using an authentication token managed by a TokenManager instance.
    This function is designed to retrieve all tags within the system.

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must
        have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the tags' information, with columns:
        - id: Tag's unique identifier.
        - name: Tag's given name.
        - desc: Description of the tag.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request,
        or if there is a failure in parsing the JSON response.
    """
    # Retrieve Access Token and Expiration from .env file
    a_token = token.get_token()

    # API Cloud URL
    url_cloud = token.url_cloud  # Make sure this is a property or method that exists

    # Create URL for request
    url = f"{url_cloud}/tags"

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
    