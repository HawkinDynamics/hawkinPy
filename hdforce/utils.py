import pandas as pd
from pandas import json_normalize
import requests
import datetime
import logging

class TokenManager:
    """Manages authentication tokens for accessing an API, including token retrieval and refresh.

    Parameters
    ----------
    refresh_token : str
        The refresh token used to obtain access tokens.

    region : str, optional
        The geographic region associated with the API endpoint. Defaults to "Americas", with other options being "Europe" and "Asia/Pacific".

    Attributes
    ----------
    refresh_token : str
        Stores the refresh token.

    region : str
        Stores the region.

    token : str or None
        Stores the current access token.

    token_expiration : datetime.datetime or None
        Stores the expiration time of the current access token.

    url_cloud : str or None
        Stores the base URL for the API corresponding to the region.
    """

    def __init__(self, refreshToken, region="Americas"):
        self.refreshToken = refreshToken
        self.region = region
        self.token = None
        self.token_expiration = None
        self.url_cloud = None
        self.get_access()
        self.get_token()

    def get_access(self):
        """Fetches and stores a new access token using the refresh token, updates the token expiration, and sets the API base URL based on the region.

        Raises
        ------
        ValueError
            If the API response indicates an error with the refresh token or connection issues.
        """
        url_token = {
            "Americas": "https://cloud.hawkindynamics.com/api/token",
            "Europe": "https://eu.cloud.hawkindynamics.com/api/token",
            "Asia/Pacific": "https://apac.cloud.hawkindynamics.com/api/token"
        }.get(self.region, "https://cloud.dev.hawkindynamics.com/api/token")

        self.url_cloud = {
            "Americas": "https://cloud.hawkindynamics.com/api/dev",
            "Europe": "https://eu.cloud.hawkindynamics.com/api/dev",
            "Asia/Pacific": "https://apac.cloud.hawkindynamics.com/api/dev"
        }.get(self.region, "https://cloud.dev.hawkindynamics.com/api/dev")

        headers = {"Authorization": f"Bearer {self.refreshToken}"}
        response = requests.get(url_token, headers=headers)

        if response.status_code == 200:
            token_response = response.json()
            self.token = token_response['access_token']
            self.token_expiration = datetime.datetime.fromtimestamp(token_response['expires_at'])
            logging.info(f"Access token retrieved and will expire at {self.token_expiration}.")
        else:
            error_msg = {
                401: "Error 401: Refresh Token is invalid or expired.",
                403: "Error 403: Refresh Token is missing",
                500: "Error 500: Something went wrong. Please contact support@hawkindynamics.com"
            }.get(response.status_code, f"Unexpected response code: {response.status_code}")

            logging.error(error_msg)
            raise ValueError(error_msg)

    def get_token(self):
        """Returns the current access token, refreshing it if necessary based on expiration.

        Returns
        -------
        str
            The current, valid access token.

        Raises
        ------
        ValueError
            If there is a failure in refreshing the token due to API errors.
        """
        if self.token is None or self.token_expiration <= datetime.datetime.now():
            self.get_access()
        return self.token

def responseHandler(json_data):
    """Parses and arranges the JSON response from the API into a structured Pandas DataFrame.

    Parameters
    ----------
    json_data : dict
        A dictionary containing nested JSON data.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing columns for id, name, teams, groups, active, and external,
        arranged according to a custom-defined order.

    """
    # Normalize the 'athlete' data from each entry in 'data'
    df = json_normalize(json_data['data'], errors='ignore')

    # List all columns from the DataFrame
    columns = df.columns.tolist()

    # Custom order function to prioritize certain columns
    def custom_order(col):
        if col == 'id':
            return 0
        elif col == 'timestamp':
            return 1
        elif col.startswith('athlete'):
            return 2
        elif col == 'active':
            return 3
        elif col.startswith('testType'):
            return 4
        elif col == 'segment':
            return 5
        else:
            return 6

    # Sort columns based on custom order
    sorted_columns = sorted(columns, key=custom_order)

    # Rearrange DataFrame using sorted column names
    df = df[sorted_columns]

    return df
