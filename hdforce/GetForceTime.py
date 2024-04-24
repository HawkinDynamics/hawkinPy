# Create function to call tests by type
import requests
import pandas as pd

#--------------------#
## Get Force Time
def GetForceTime(token, testId: str) -> pd.DataFrame:
    """Fetches and returns raw force-time data for an individual test trial from an API,
    using an authentication token managed by a TokenManager instance.

    Parameters
    ----------
    token : TokenManager
        An instance of TokenManager which handles authentication. This object must
        have `get_token` and `url_cloud` methods to fetch the access token and the API URL, respectively.

    testId : str
        The unique ID given to each test trial.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing detailed information about the test trial, with columns:
        - Time (s): Time elapsed in seconds.
        - LeftForce (N): Force at time point through left plate.
        - RightForce (N): Force at time point through right plate.
        - CombinedForce (N): Combined force (Left + Right) at each time point.
        - Velocity (m/s): Calculated center of mass velocity at each time point.
        - Displacement (m): Calculated center of mass displacement from starting height at each time point.
        - Power (W): Calculated power of mass at each time point.
        - RSI: Calculated Reactive Strength Index (if applicable).

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request,
        or if there is a failure in parsing the JSON response.
    ValueError
        If the 'testId' parameter is not a string.
    """

   # Retrieve Access Token and check expiration
    a_token = token.get_token() 

    # API Cloud URL
    url_cloud = token.url_cloud

    # Test ID
    if isinstance(testId, str):
        tid = testId
    else:
        raise ValueError("Error: TestId must be a string")

    # Create URL for request
    url = f"{url_cloud}/forcetime/{tid}"

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    # Check response status and handle data accordingly
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.reason}")

    try:
        # Flatten test data from response
        data = response.json()
        # Create DataFrame from the array data
        df = pd.DataFrame({
            "Time(s)": data["Time(s)"],
            "LeftForce(N)": data["LeftForce(N)"],
            "RightForce(N)": data["RightForce(N)"],
            "CombinedForce(N)": data["CombinedForce(N)"],
            "Velocity(m/s)": data["Velocity(m/s)"],
            "Displacement(m)": data["Displacement(m)"],
            "Power(W)": data["Power(W)"],
            "rsi": [data["rsi"]] * len(data["Time(s)"])  # Assuming rsi is a constant value
        })

        # Setting attributes
        df.attrs['Test ID'] = data['id']
        df.attrs['Test Name'] = data['testType']['name']
        df.attrs['Athlete Name'] = data['athlete']['name']
        df.attrs['Athlete ID'] = data['athlete']['id']
        df.attrs['Timestamp'] = pd.to_datetime(data['timestamp'], unit='s')
        df.attrs['RSI'] = data['rsi']

            
        return df
    except ValueError:
        raise Exception("Failed to parse JSON response or no data returned.")
    