#import pandas as pd
from pandas import json_normalize
import requests
import datetime
import logging
import os
from dotenv import load_dotenv, set_key


#--------------------#
# Logger
# Create a logger
logger = logging.getLogger('hdforce')
logger.setLevel(logging.DEBUG)  # Set minimum level of logs to capture

# Create file handler which logs even debug messages
fh = logging.FileHandler('hdforce.log')
fh.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


#--------------------#
# Configuration Manager
#config_manager_code 
class ConfigManager:
    # Class to manage configuration for environment variables source
    env_method = 'env'  # Default to system environment variables
    file_name = None

    @classmethod
    def set_env_source(cls, region, method, fileName, token_name, token):
        # Set the source of environment variables ('file' or 'system')
        if method not in ['file', 'env', 'manual']:
            logger.error("::set_env_source:: Source must be 'file', 'env', or 'manual'")
            raise ValueError("Source must be 'file', 'env', or 'manual'.")
        cls.env_method = method

        # Set the .env file name
        if method == 'file':
            if not fileName:
                logger.error("::set_env_source:: File path must be provided when source is 'file'")
                raise ValueError("File path must be provided when source is 'file'")
            cls.file_name = fileName
        
        # Set other Auth arguments
        cls.token_name = token_name     # Refresh Token Name
        cls.refresh_token = token       # Refresh Token
        cls.region = region             # Region

        

    @classmethod
    def get_env_variable(cls, var_name):
        # Get an environment variable from the specified source
        if cls.env_method == 'file':
            if not cls.file_name:
                logger.error("::get_env_variable:: File path must be provided when source is 'file'")
                raise ValueError("File path must be provided when source is 'file'")
            from dotenv import load_dotenv
            import os
            load_dotenv(cls.file_name)
            return os.getenv(var_name)
        else:
            import os
            return os.getenv(var_name)


#--------------------#
# Variable Manager
def varsManager( name: str, method: str, file: str = None, value: str = None) -> str:
    """ Get or set a token value

    Parameters
    ----------
    name : str
        name the variable you want to create or retrieve

    value : str
        the value to be stored
    """
    # Load environment file if necessary
    if method == 'file':
        load_dotenv(str(file))
        if value is not None:
            set_key(str(file),str(name), str(value))
            token = value
        else:
            token = os.getenv(str(name))
    else:
        if value is not None:
            os.environ[str(name)] = str(value)
            token = value
        else:
            token = os.getenv(str(name))

    return(token)


#--------------------#
# Token Manager Class
class TokenManager:
    """Manages authentication tokens for accessing an API, including token retrieval and refresh.

    Parameters
    ----------
    refreshToken : str
        The refresh token used to obtain access tokens.

    region : str
        The geographic region associated with the API endpoint. Defaults to "Americas", with other options being "Europe" and "Asia/Pacific".

    Attributes
    ----------
    refreshToken : str
        Stores the refresh token.

    region : str
        Stores the region.

    accessToken : str or None
        Stores the current access token.

    ExpirationVal : datetime.datetime or None
        Stores the expiration time of the current access token as an int

    ExpirationStr : datetime.datetime or None
        Stores the expiration time of the current access token as an timestamp

    url_cloud : str or None
        Stores the base URL for the API corresponding to the region.
    """
    # Class attributes
    def __init__(self, refreshToken, region):
            self.refreshToken = refreshToken
            self.region = region
            self.accessToken = None
            self.ExpirationVal = None
            self.ExpirationStr = None
            self.url_cloud = None
            self.get_access()

    # Get access token and exp
    def get_access(self):
        """Fetches and stores a new access token using the refresh token."""
        # Set Token Request URL
        url_token = {
            "Americas": "https://cloud.hawkindynamics.com/api/token",
            "Europe": "https://eu.cloud.hawkindynamics.com/api/token",
            "Asia/Pacific": "https://apac.cloud.hawkindynamics.com/api/token"
        }.get(self.region, "https://cloud.dev.hawkindynamics.com/api/token")

        # Set Cloud URL
        self.url_cloud = {
            "Americas": "https://cloud.hawkindynamics.com/api/dev",
            "Europe": "https://eu.cloud.hawkindynamics.com/api/dev",
            "Asia/Pacific": "https://apac.cloud.hawkindynamics.com/api/dev"
        }.get(self.region, "https://cloud.dev.hawkindynamics.com/api/dev")

        # Set auth headers
        headers = {"Authorization": f"Bearer {self.refreshToken}"}
        # Send Token Request
        response = requests.get(url_token, headers=headers)

        # Handle request response
        if response.status_code == 200:  # successfull
            token_response = response.json()
            self.accessToken = token_response['access_token']
            self.ExpirationStr = datetime.datetime.fromtimestamp(token_response['expires_at'])
            self.ExpirationVal = int(token_response['expires_at'])
            logger.debug(f"::TokenManaer:: Access token retrieved successfully")
        else:  # error
            error_msg = {
                401: "Error 401: Refresh Token is invalid or expired.",
                403: "Error 403: Refresh Token is missing",
                500: "Error 500: Something went wrong. Please contact support@hawkindynamics.com"
            }.get(response.status_code, f"Unexpected response code: {response.status_code}")
            logger.error(error_msg)
            raise ValueError(error_msg)


#--------------------#
# Response Handler for test calls
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
