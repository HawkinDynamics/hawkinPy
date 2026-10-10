# Dependencies -----
import requests
import os
from typing import List
# Package imports
from .utils import logger, ensure_token, auth_headers
from .Classes import NewAthlete, AthleteResult, athlete_payloads

# -------------------- #
# Create Athletes


def CreateAthletes(athletes: List[NewAthlete]) -> List[AthleteResult]:
    """Create athletes for your account. Up to 500 at one time.

    Parameters
    ----------
    athletes : list[NewAthlete]
        A list of NewAthlete objects to create. The optional profile fields
        `position`, `sport`, `dob` and `height` are sent as native athlete
        fields (never inside `external`). `dob` accepts a `datetime.date`,
        a 4-digit year or 'YYYY-MM-DD'; `height` is in centimeters
        (rounded to 1 decimal place; the API rejects values outside 0 to
        300, and 0 is not sent). Fields left as None
        are not sent and stay unset.

    Returns
    -------
    list[AthleteResult]
        A list of AthleteResult objects indicating success or failure
        for each athlete.

    Raises
    ------
    Exception
        If the HTTP response status is not 200.

    Warns
    -----
    UserWarning
        If any athlete has a height below 100. The API reads such values
        back as legacy feet/inches (e.g. 95 reads back as 241.3).
    """
    a_token = ensure_token()
    url_cloud = os.getenv("CLOUD_URL")
    url = f"{url_cloud}/athletes/bulk"
    payload = athlete_payloads(athletes)

    logger.debug(f"Payload: {len(payload)} athletes")
    headers = auth_headers(a_token)
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(
            f"Error {response.status_code}: {response.reason}"
        )

    response_data = response.json()
    data = response_data.get('data', [])
    failures = response_data.get('failures', [])

    # Build name->id mapping from successful creates
    success_map = {a['name']: a.get('id', '') for a in data}

    # Build name->reason mapping from failures
    failure_map = {}
    for f in failures:
        name = f.get('data', {}).get('name', 'Unknown')
        reason = f.get('reason', 'Unknown error')
        failure_map[name] = reason

    # Build AthleteResult list
    results = []
    for athlete in athletes:
        if athlete.name in success_map:
            results.append(AthleteResult(
                name=athlete.name,
                id=success_map[athlete.name],
                successful=True,
                reason=[]
            ))
        elif athlete.name in failure_map:
            results.append(AthleteResult(
                name=athlete.name,
                id='',
                successful=False,
                reason=[failure_map[athlete.name]]
            ))
        else:
            results.append(AthleteResult(
                name=athlete.name,
                id='',
                successful=False,
                reason=["Unknown error"]
            ))

    successful_count = sum(1 for r in results if r.successful)
    logger.info(
        f"Request successful. Athletes created: {successful_count}"
    )
    return results
