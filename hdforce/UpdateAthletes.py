# Dependencies -----
import requests
import os
import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
# Package imports
from .AuthManager import AuthManager
from .utils import ConfigManager
from .LoggerConfig import LoggerConfig
from .Classes import Athlete, AthleteResult

# Get a logger specific to this module
logger = LoggerConfig.get_logger(__name__)

# -------------------- #
# Update Athletes

def UpdateAthletes(athletes: List[Athlete]) -> List[AthleteResult]:
    """Update athletes for your account. Up to 500 at one time.

    Parameters
    ----------
    athletes : list[Athlete]
        A list of Athletes with class of `Athlete`.

    Returns
    -------
    list[AthleteResult]
        A list of AthleteResult objects indicating the success or failure of each athlete creation.

    Raises
    ------
    Exception
        If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.
    """
    # Retrieve Access Token and check expiration
    a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
    tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))

    # get current time in timestamp
    now = datetime.datetime.now()
    nowtime = datetime.datetime.timestamp(now)

    # Validate refresh token and expiration
    if a_token is None:
        logger.error("No Access Token found.")
        raise Exception("No Access Token found.")
    elif int(nowtime) >= tokenExp:
        logger.debug(f"Token Expired: {datetime.datetime.fromtimestamp(tokenExp)}")
        # authenticate
        try:
            AuthManager(
                region=ConfigManager.region,
                authMethod=ConfigManager.env_method,
                refreshToken_name=ConfigManager.token_name,
                refreshToken=ConfigManager.refresh_token,
                env_file_name=ConfigManager.file_name
            )
            # Retrieve Access Token and check expiration
            a_token = ConfigManager.get_env_variable("ACCESS_TOKEN")
            logger.debug("New ACCESS_TOKEN retrieved")
            tokenExp = int(ConfigManager.get_env_variable("TOKEN_EXPIRATION"))
            logger.debug("TOKEN_EXPIRATION retrieved")
            if a_token is None:
                logger.error("No Access Token found.")
                raise Exception("No Access Token found.")
            elif int(nowtime) >= tokenExp:
                logger.debug(f"Token Expired: {datetime.datetime.fromtimestamp(tokenExp)}")
                raise Exception("Token expired")
            else:
                logger.debug(f"New Access Token valid through: {datetime.datetime.fromtimestamp(tokenExp)}")
                pass
        except ValueError:
            logger.error("Failed to authenticate. Try AuthManager")
            raise Exception("Failed to authenticate. Try AuthManage")
    else:
        logger.debug(f"Access Token retrieved. expires {datetime.datetime.fromtimestamp(tokenExp)}")

    # API Cloud URL
    url_cloud = os.getenv("CLOUD_URL")

    # GET Request
    headers = {"Authorization": f"Bearer {a_token}"}

    # Determine URL and payload based on the number of athletes
    url = f"{url_cloud}/athletes/bulk"
    payload = [athlete.model_dump() for athlete in athletes]

    # Log the payload being sent
    logger.debug(f"Payload being sent to API: {payload}")

    # GET Request
    response = requests.put(url, headers=headers, json=payload)

    # Response Handling
    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(f"Error {response.status_code}: {response.reason}")
    
    try:
        response_data = response.json()
        data = response_data.get('data', [])
        failures = response_data.get('failures', [])
    
        # Successful athlete names
        successful_names = [athlete['name'] for athlete in data]
    
        # Process failures into a dictionary of name to reason
        failure_reasons = {failure['data']['name']: failure['reason'] for failure in failures}
    
        # Create a list of AthleteResult objects
        results = []
        for athlete in athletes:
            if athlete.name in successful_names:
                results.append(AthleteResult(name=athlete.name, id=athlete.id, successful=True, reason=[]))
            elif athlete.name in failure_reasons:
                results.append(AthleteResult(name=athlete.name, id=athlete.id, successful=False, reason=[failure_reasons[athlete.name]]))
            else:
                results.append(AthleteResult(name=athlete.name, id=athlete.id, successful=False, reason=["Unknown error"]))
    
        # Log the successful athletes count
        successful_count = sum(result.successful for result in results)
        logger.info(f"Request successful. Athletes updated: {successful_count}")
    
        return results
    
    except ValueError:
        logger.error("Failed to parse JSON response or no data returned.")
        raise Exception("Failed to parse JSON response or no data returned.")