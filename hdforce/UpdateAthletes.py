# Dependencies -----
import requests
import os
from typing import List
# Package imports
from .utils import logger, ensure_token, auth_headers
from .Classes import Athlete, AthleteResult, athlete_payloads

# -------------------- #
# Update Athletes


def UpdateAthletes(athletes: List[Athlete]) -> List[AthleteResult]:
    """Update athletes for your account. Up to 500 at one time.

    Parameters
    ----------
    athletes : list[Athlete]
        A list of Athlete objects with required id and name fields. Only
        the fields you set are sent; any field you don't set (active,
        teams, groups, external, profile fields) is left UNCHANGED. A field
        you set explicitly is sent even if it equals the default, e.g.
        `teams=[]` removes the athlete from all teams. The optional profile
        fields `position`, `sport`, `dob` and `height` are sent as native
        athlete fields (never inside `external`), with the same formats as
        `NewAthlete`. Fields set to None are not sent and are left
        UNCHANGED; the API cannot clear them (clear them in the Hawkin
        app). `lastTestedOn` is read-only and never sent. `external`, when
        you send it, is replaced, not merged: any custom property you leave
        out of it is deleted.

    Returns
    -------
    list[AthleteResult]
        A list of AthleteResult objects indicating success or failure
        for each athlete update.

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
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(
            f"Error {response.status_code}: {response.reason}"
        )

    response_data = response.json()
    data = response_data.get('data', [])
    failures = response_data.get('failures', [])

    # Attribute results by id, not name. Two athletes in one batch can share
    # a name, and keying on name collapses their results: a failed update can
    # be reported as successful, and the wrong athlete can get the reason.
    # Athlete.id is required, the API returns it on each success and echoes
    # the input it rejected in failures[].data, so the id is on every path.
    # Name stays as a fallback for a response entry that arrives without one.
    successful_ids = {a['id'] for a in data if a.get('id')}
    successful_names = {a['name'] for a in data if not a.get('id')}

    failure_by_id = {}
    failure_by_name = {}
    for f in failures:
        sent = f.get('data') or {}
        if sent.get('id'):
            failure_by_id[sent['id']] = f['reason']
        elif sent.get('name'):
            failure_by_name[sent['name']] = f['reason']

    # The names are a fallback for a response with no ids anywhere, not a
    # second lookup beside the ids. Mixing the two would reopen the same
    # collapse: an id-less success entry would mark every same-named athlete
    # successful, including one the failures list rejected by id. When the
    # response does carry ids, an athlete it never mentions is reported as an
    # unknown error rather than guessed at by name.
    use_names = not successful_ids and not failure_by_id

    # Build AthleteResult list
    results = []
    for athlete in athletes:
        if athlete.id in successful_ids or (
            use_names and athlete.name in successful_names
        ):
            results.append(AthleteResult(
                name=athlete.name,
                id=athlete.id,
                successful=True,
                reason=[]
            ))
            continue

        reason = failure_by_id.get(athlete.id)
        if reason is None and use_names:
            reason = failure_by_name.get(athlete.name)
        results.append(AthleteResult(
            name=athlete.name,
            id=athlete.id,
            successful=False,
            reason=[reason if reason is not None else "Unknown error"]
        ))

    successful_count = sum(1 for r in results if r.successful)
    logger.info(
        f"Request successful. Athletes updated: {successful_count}"
    )
    return results
