import requests
import pandas as pd

def GetTypes(token) -> pd.DataFrame:
    """Fetches and returns the test type names and IDs from an API, using an authentication token managed by a TokenManager instance.

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must
        have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the test types, with columns:
        - id: The unique identifier for each test type.
        - name: The name of each test type.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request,
        or if there is a failure in parsing the JSON response.
    """
    # Retrieve the access token and check its expiration
    a_token = token.get_token()

    # Retrieve the cloud URL from the token manager
    url_cloud = token.url_cloud

    # Construct the API endpoint URL
    url = f"{url_cloud}/test_types"

    # Setup the authorization headers for the API request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Send the GET request to the API
    response = requests.get(url, headers=headers)

    # Check if the API response was successful
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.reason}")

    # Try to parse the JSON data returned by the API
    try:
        data = response.json()
        df = pd.DataFrame.from_records(data)
        return df
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")
