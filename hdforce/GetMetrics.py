# Dependencies -----
import requests
import pandas as pd

def GetMetrics(token) -> pd.DataFrame:
    """
    Fetches and returns test metrics from an API, using an authentication token managed by a TokenManager instance.

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the test metrics, with columns:
        - id: The unique identifier for each metric.
        - name: The name of each metric.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    """

    # Retrieve Access Token and check expiration
    a_token = token.get_token()

    # API Cloud URL
    url_cloud = token.url_cloud  # Make sure this is a property or method that exists

    # Create URL for request
    url = f"{url_cloud}/metrics"  # Note: Removed the underscore from "/test_Types" to "/test_types"

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
        # Flatten test data from response
        data = response.json()
        # Create DataFrame from JSON
        df = pd.DataFrame(data)

        # Explode 'metrics' column to expand each list element into a row
        df = df.explode('metrics')

        # Normalize 'metrics' column
        metrics_df = pd.json_normalize(df['metrics'])

        # Concatenate the original DataFrame with the normalized metrics DataFrame
        result_df = pd.concat([df.drop('metrics', axis=1).reset_index(drop=True), metrics_df], axis=1)

        return(result_df)
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")