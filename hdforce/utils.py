# Dependencies
import pandas as pd
from pandas import json_normalize
import requests
import datetime
import os
from dotenv import load_dotenv, set_key
from .LoggerConfig import LoggerConfig

# Get a logger specific to this module
logger = LoggerConfig.get_logger(__name__)

# -------------------- #
# Configuration Manager


class ConfigManager:
    # Class to manage configuration for environment variables source
    env_method = 'env'  # Default to system environment variables
    file_name = None

    @classmethod
    def set_env_source(self, region, method, fileName, token_name, token):
        # Set the source of environment variables ('file' or 'system')
        if method not in ['file', 'env', 'manual']:
            logger.error("Source must be 'file', 'env', or 'manual'")
            raise ValueError("Source must be 'file', 'env', or 'manual'.")

        self.env_method = method
        logger.debug(f"method: {method}")

        # Set the .env file name
        if method == 'file':
            if not fileName:
                logger.error("File path must be provided when source is 'file'")
                raise ValueError("File path must be provided when source is 'file'")
            self.file_name = fileName
            logger.debug(f"file name: {fileName}")

        # Set other Auth arguments
        self.token_name = token_name     # Refresh Token Name
        logger.debug(f"token name: {token_name}")
        self.refresh_token = token       # Refresh Token
        tabrv = token[0:6]
        logger.debug(f"refresh token: {tabrv}xxxx")
        self.region = region             # Region
        logger.debug(f"region: {region}")

    @classmethod
    def get_env_variable(self, var_name):
        # Get an environment variable from the specified source
        if self.env_method == 'file':
            if not self.file_name:
                logger.error("File path must be provided when source is 'file'")
                raise ValueError("File path must be provided when source is 'file'")
            from dotenv import load_dotenv
            import os
            load_dotenv(self.file_name, override=True)
            return os.getenv(var_name)
        else:
            import os
            return os.getenv(var_name)


# -------------------- #
# Variable Manager


def varsManager(name: str, method: str, file: str = None, value: str = None) -> str:
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
        if value is not None:
            set_key(str(file), str(name), str(value))
            logger.debug(f"Key Set: file({str(file)}) | name({str(name)}) | value({str(value)})")
            load_dotenv(str(file), override=True)
            token = str(value)
            logger.debug(f"token: {value}")
        else:
            token = os.getenv(str(name))
    else:
        if value is not None:
            os.environ[str(name)] = str(value)
            logger.debug(f"Key Set: env | name({str(name)}) | value({str(value)})")
            token = str(value)
            logger.debug(f"token: {os.getenv(str(value))}")
        else:
            token = os.getenv(str(name))
            logger.debug(f"token: {os.getenv(str(name))}")

    return token


# -------------------- #
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
    def __init__(self, refreshToken, region, fileName):
        self.refreshToken = refreshToken
        self.region = region
        self.accessToken = None
        self.ExpirationVal = None
        self.ExpirationStr = None
        self.url_cloud = None
        self.fileName = fileName
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
        if response.status_code == 200:  # successful
            token_response = response.json()
            self.accessToken = token_response['access_token']
            self.ExpirationStr = datetime.datetime.fromtimestamp(token_response['expires_at'])
            self.ExpirationVal = int(token_response['expires_at'])
            # Debug logs
            if int(datetime.datetime.timestamp(datetime.datetime.now())) >= self.ExpirationVal:
                logger.debug(f"Fail |Access token expired: {self.ExpirationVal}")
            else:
                logger.debug(f"Pass | Access token retrieved successfully. Expires: {self.ExpirationVal}")
        else:  # error
            error_msg = {
                401: "Error 401: Refresh Token is invalid or expired.",
                403: "Error 403: Refresh Token is missing",
                500: "Error 500: Something went wrong. Please contact support@hawkindynamics.com"
            }.get(response.status_code, f"Unexpected response code: {response.status_code}")
            logger.error(error_msg)
            raise ValueError(error_msg)


# -------------------- #
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
    # 1 - Create normalized DataFrame
    dfAll = json_normalize(json_data['data'], errors='ignore')
        

    # 2 - Remove athlete and testType columns
    # 2.1 - Generate a list of columns to drop
    columns_to_drop = [col for col in dfAll.columns if col.startswith('testType') or col.startswith('athlete')]

    # 2.2 - Drop the columns from the DataFrame
    dfAll.drop(columns=columns_to_drop, inplace=True)

    # 3.1 - Create DataFrame of athlete and testType info
    infoDF = pd.json_normalize(
            json_data['data'],
            meta=[
                'id',
                ['athlete', 'id'],
                ['athlete', 'name'],
                ['athlete', 'teams'],
                ['athlete', 'groups'],
                ['athlete', 'active'],
                ['testType', 'id'],
                ['testType', 'name'],
                ['testType', 'canonicalId']
            ], errors='ignore'
        )

    # 4.3 - Create DataFrame of tags column from infoDF
    tags = pd.DataFrame(infoDF["testType.tags"])
    
    # 3.2 - Extract only athlete and testType data
    selected_columns = infoDF.columns[infoDF.columns.astype(str).str.startswith('athlete') | infoDF.columns.astype(str).str.startswith('testType')]

    # 3.3 Narrow down the DataFrame
    infoDF = infoDF[selected_columns]

    # 4- Create data frame of tags from testType.tags
    # 4.1 - Function to extract IDs
    def extract_ids(tags):
        return [tag['id'] for tag in tags if 'id' in tag]

    # 4.2 - Function to extract names
    def extract_names(tags):
        return [tag['name'] for tag in tags if 'name' in tag]

    # 4.3 - Create DataFrame of tags column from infoDF
        tags = pd.DataFrame(infoDF["testType.tags"])

    # 4.4 - Apply these functions to create new columns in tags
    tags['tag_ids'] = tags['testType.tags'].apply(extract_ids)
    tags['tag_names'] = tags['testType.tags'].apply(extract_names)

    # 4.5 - Drop the original column from the tags DataFrame
    tags = tags.drop(columns="testType.tags", axis=1)

    # 5 - Remove testType.tags from infoDF DataFrame
    infoDF = infoDF.drop(columns="testType.tags", axis=1)

    # 6 - Join New DataFrames together
    df = dfAll.join(infoDF).join(tags)

    # 7 - change "." to "_" in column names
    df.columns = [col.replace('.', '_') for col in df.columns]

    # 8 - List all columns from the DataFrame
    columns = df.columns.tolist()

    # 9 - Custom order function to prioritize certain columns
    def custom_order(col):
        if col == 'id':
            return 0
        elif col == 'timestamp':
            return 1
        elif col.startswith('athlete'):
            return 2
        elif col == 'active':
            return 7
        elif col.startswith('testType'):
            return 3
        elif col.startswith('tag'):
            return 4
        elif col == 'segment':
            return 5
        else:
            return 6

    # 10 - Sort columns based on custom order
    sorted_columns = sorted(columns, key=custom_order)

    # 11 - Rearrange DataFrame using sorted column names
    df = df[sorted_columns]

    # 12 - change "athlete_external_" to "external_" in column names
    df.columns = [col.replace('athlete_external_', 'external_') for col in df.columns]

    return df


# -------------------- #
# Deprecation Decorator

import warnings
import functools

def deprecated(reason):
    """
    Decorator to mark functions as deprecated.
    
    Args:
        reason (str): The reason why the function is deprecated and what to use instead.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"Function {func.__name__} is deprecated: {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator
