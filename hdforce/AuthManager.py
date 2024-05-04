import os
from dotenv import load_dotenv, set_key
# Package imports
from .LoggerConfig import LoggerConfig
from .utils import TokenManager, varsManager, ConfigManager

# Get a logger specific to this module
logger = LoggerConfig.get_logger(__name__)

# -------------------- #
# Authenticator


def AuthManager(authMethod: str = "env", refreshToken_name: str = "HD_REFRESH_TOKEN", refreshToken: str = None, env_file_name: str = None, region: str = "Americas") -> None:
    """ Choose the authentication settings


    Parameters
    ----------
    region : str required
        The region that designates the url prefix.

    authMethod : str required
        Determine method of storing authentication variables, including refresh token. One of 'env', 'file', 'manual'. env = use of system environment. file = use of .env file. manual = no stored refresh token.

    refreshToken_name : str
        Specific name of refresh token variable saved in system environment or .env file

    refreshToken : str
        If used with authMethod='manual', token will be used to authenticate without being stored. Else token will be used set as the new refresh token value with method selected.

    env_file_name : str
        Required with authMethod='file'. Provides file name for variable storage.


    Raises
    ------
    ValueError
        If authMethod not one of env, file, or method.
        If authMethod = 'file' and no file name provided
        If authMethod='manual' and no refreshToken provided

    """
    # auth method options
    methods = ['env', 'file', 'manual']

    # Check for valid method choice
    if authMethod not in methods:
        logger.error(f"{authMethod} is invalid authentication method.")
        raise ValueError(f"Invalid auth method. Allowed methods are: {methods}")
    else:
        logger.debug(f"Authentication method selected: {authMethod}.")

    # Load environment file if necessary
    if authMethod == 'file':
        if env_file_name:
            load_dotenv(str(env_file_name), override=True)
            logger.debug(f"Environment variables loaded from {env_file_name}.")
        else:
            logger.error("No file name given")
            raise ValueError("No file name given. Must be provided with authMethod='file'")

    # Retrieve or set the refresh token
    if authMethod == 'manual':
        if refreshToken is None:
            logger.error("No refresh token found given")
            raise ValueError("Refresh token must be provided with 'manual' authentication method.")
        else:
            key = refreshToken
            kabrv = key[0:6]
            #logger.debug(f"Manual auth method used with token {kabrv}xxxx")
    else:
        key = varsManager(name=refreshToken_name, value=refreshToken, method=authMethod, file=env_file_name)
        kabrv = key[0:6]
        logger.debug(f"Refresh token: {kabrv}xxxx method: {authMethod}")

    # Setup session assuming TokenManager handles authentication
    session = TokenManager(refreshToken=key, region=region, fileName=env_file_name)

    # Create objects of classes
    accessToken = str(session.accessToken)
    tokenExpiration = str(session.ExpirationVal)
    expirationStr = str(session.ExpirationStr)
    cloudURL = str(session.url_cloud)
    fileName = str(session.fileName)

    if authMethod == 'file':
        load_dotenv(str(fileName), override=True)

        # Set environment variables
        set_key(fileName, "ACCESS_TOKEN", accessToken)
        # Environment variable debugging: Access Token
        if accessToken == os.getenv("ACCESS_TOKEN"):
            logger.debug(f"New Access Token Set")
        else:
            logger.debug(f"Error: new token not found")

        # Environment variable debugging: Token Expiration
        set_key(fileName, "TOKEN_EXPIRATION", tokenExpiration)
        if tokenExpiration == os.getenv("TOKEN_EXPIRATION"):
            logger.debug(f"New expiration Set")
        else:
            logger.debug(f"Error: new expiration not passed")

        # Environment variable debugging: Cloud URL
        set_key(fileName, "CLOUD_URL", cloudURL)
        if cloudURL == os.getenv("CLOUD_URL"):
            logger.debug(f"New URL set")
        else:
            logger.debug(f"Error: new URL not passed")

    else:
        # Environment variable debugging: Access Token
        os.environ['ACCESS_TOKEN'] = accessToken
        if accessToken == os.getenv("ACCESS_TOKEN"):
            logger.debug(f"New Access Token Set")
        else:
            logger.debug(f"Error: new token not found")

        # Environment variable debugging: Token Expiration
        os.environ['TOKEN_EXPIRATION'] = tokenExpiration
        if tokenExpiration == os.getenv("TOKEN_EXPIRATION"):
            logger.debug(f"New expiration Set")
        else:
            logger.debug(f"Error: new expiration not passed")

        # Environment variable debugging: Cloud URL
        os.environ['CLOUD_URL'] = cloudURL
        if cloudURL == os.getenv("CLOUD_URL"):
            logger.debug(f"New URL set")
        else:
            logger.debug(f"Error: new URL not passed")

    # Set environment source in ConfigManager based on authMethod
    if authMethod == 'file':
        # Check if filename passed
        if not isinstance(fileName, str):
            logger.error("File path must be provided when source is 'file'")
            raise ValueError("File path must be provided when source is 'file'")
        # if filename exists and string initialize dotenv
        load_dotenv(str(fileName), override=True)
        # run configuration manager
        ConfigManager.set_env_source(region=region, method=authMethod, fileName=fileName, token_name=refreshToken_name, token=key)
        logger.debug(f"ConfigManager methods passed with file env: {fileName}")

    # Using environment variables
    elif authMethod == 'env' or 'manual':
        # run configuration manager
        ConfigManager.set_env_source(region=region, method=authMethod, fileName=fileName, token_name=refreshToken_name, token=key)
        logger.debug(f"ConfigManager methods passed with {authMethod} method")

    # Alert of missing variables
    else:
        # List to hold the names of empty variables
        empty_variables = []

        # Check each variable and add the name to the list if it is empty
        if not accessToken:
            empty_variables.append("Access Token")
        if not tokenExpiration:
            empty_variables.append("token Expiration")
        if not cloudURL:
            empty_variables.append("Cloud URL")

        # Create a message based on which variables are empty
        if empty_variables:
            # Join the names of the empty variables into a comma-separated string
            empty_vars_str = ", ".join(empty_variables)
            logger.error(f"Missing variables: {empty_vars_str}.")
            raise ValueError(f"The following variables are empty: {empty_vars_str}.")
