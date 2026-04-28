# Dependencies -----
import requests
import os
from typing import List
# Package imports
from .utils import logger, ensure_token
from .Classes import Athlete, AthleteResult

# -------------------- #
# Update Athletes


def UpdateAthletes(athletes: List[Athlete]) -> List[AthleteResult]:
    """Update athletes for your account. Up to 500 at one time.

    Parameters
    ----------
    athletes : list[Athlete]
        A list of Athlete objects with required id field.

    Returns
    -------
    list[AthleteResult]
        A list of AthleteResult objects indicating success or failure
        for each athlete update.

    Raises
    ------
    Exception
        If the HTTP response status is not 200.
    """
    a_token = ensure_token()
    url_cloud = os.getenv("CLOUD_URL")
    url = f"{url_cloud}/athletes/bulk"
    payload = [athlete.model_dump() for athlete in athletes]

    logger.debug(f"Payload: {len(payload)} athletes")
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(
            f"Error {response.status_code}: {response.reason}"
        )

    response_data = response.json()
    data = response_data.get('data', [])
    failures = response_data.get('failures', [])

    # Build name->reason mapping from failures
    failure_map = {
        f['data']['name']: f['reason'] for f in failures
    }

    # Build AthleteResult list
    successful_names = [a['name'] for a in data]
    results = []
    for athlete in athletes:
        if athlete.name in successful_names:
            results.append(AthleteResult(
                name=athlete.name,
                id=athlete.id,
                successful=True,
                reason=[]
            ))
        elif athlete.name in failure_map:
            results.append(AthleteResult(
                name=athlete.name,
                id=athlete.id,
                successful=False,
                reason=[failure_map[athlete.name]]
            ))
        else:
            results.append(AthleteResult(
                name=athlete.name,
                id=athlete.id,
                successful=False,
                reason=["Unknown error"]
            ))

    successful_count = sum(1 for r in results if r.successful)
    logger.info(
        f"Request successful. Athletes updated: {successful_count}"
    )
    return results
