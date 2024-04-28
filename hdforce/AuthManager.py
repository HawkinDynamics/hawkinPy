from dotenv import load_dotenv, set_key
from .utils import TokenManager, varsManager, logger, ConfigManager

#--------------------#
# Authenticator
def AuthManager(region: str = "Americas", authMethod: str = "env", refreshToken_name: str = "HD_REFRESH_TOKEN", refreshToken: str = None, env_file_name: str = None, ) -> None:
    """ Choose the authentication settings
    
    Parameters
    ----------
    region : str required
        The region that designates the url prefix.

    authMethod : str required
        Determine method of storing authenitcation variables, including refresh token. One of 'env', 'file', 'manual'. env = use of system environment. file = use of .env file. manual = no stored refresh token. 
    
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
        logger.error("::AuthManager:: Invalid authentication method provided.")
        raise ValueError(f"Invalid auth method. Allowed methods are: {methods}")
    else:
        logger.debug(f"::AuthManager:: Authentication method selected: {authMethod}.")
    
    # Load environment file if necessary
    if authMethod == 'file':
        if env_file_name:
            load_dotenv(str(env_file_name))
            logger.debug(f"::AuthManager:: Environment variables loaded from {env_file_name}.")
        else:
            logger.error("::AuthManager:: Environment file name must be provided when using 'file' authentication method.")
            raise ValueError("Environment file name must be provided for 'file' authentication method.")
    
     # Retrieve or set the refresh token
    if authMethod == 'manual':
        if refreshToken is None:
            logger.error("::AuthManager:: Refresh token must be provided with 'manual' authentication method.")
            raise ValueError("Refresh token must be provided with 'manual' authentication method.")
        else:
            key = refreshToken
            logger.debug("::AuthManager:: Manual authentication method used with provided refresh token.")
    else:
        key = varsManager(name=refreshToken_name, value=refreshToken, method= authMethod, file= env_file_name)
        logger.debug(f"::AuthManager:: Refresh token provided using method: {authMethod}")

    # Setup session assuming TokenManager handles authentication
    session = TokenManager(refreshToken=key, region=region)

    if authMethod == 'file':
            load_dotenv(str(env_file_name))
    
    # Set environment variables
    set_key(env_file_name, "ACCESS_TOKEN", str(session.accessToken))
    set_key(env_file_name, "TOKEN_EXPIRATION", str(session.ExpirationVal))
    set_key(env_file_name, "CLOUD_URL", str(session.url_cloud))
    logger.info(f"::AuthManager:: Authentication to {session.url_cloud} successful. Session expires at {session.ExpirationStr}.")
    
    # Set environment source in ConfigManager based on authMethod
    if authMethod == 'file':
        if not env_file_name:
            logger.error("::AuthManager:: File path must be provided when source is 'file'")
            raise ValueError("File path must be provided when source is 'file'")
        ConfigManager.set_env_source(region= region, method = authMethod, fileName= env_file_name, token_name= refreshToken_name, token= key)
        logger.debug(f"::AuthManager:: Authentication args stored in class ConfigManager")
    else:
        logger.error("::AuthMethod:: Invalid authMethod provided")
        raise ValueError("Invalid authMethod provided")