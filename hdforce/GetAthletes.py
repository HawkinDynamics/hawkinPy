# Dependencies -----
import requests
import os
import pandas as pd
# Package imports
from .utils import logger, ensure_token

# -------------------- #
# Get Athletes


def GetAthletes(includeInactive: bool = False) -> pd.DataFrame:
    """Get athlete information from an account.

    Parameters
    ----------
    includeInactive : bool, optional
        Include inactive athletes in results. Default is False.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns: id, name, teams, groups, active, and
        any external.* attribute columns. When populated on the source
        record, the following optional profile columns also appear:
        image (URL string, or None if cleared), position, dob (ISO-8601
        date string), sport, height (centimeters, range [1, 300]),
        lastTestedOn (Unix epoch seconds of the most recent test
        session).

    Raises
    ------
    Exception
        If the HTTP response status is not 200.
    """
    a_token = ensure_token()
    url_cloud = os.getenv("CLOUD_URL")
    flag = "true" if includeInactive else "false"
    url = f"{url_cloud}/athletes?includeInactive={flag}"

    logger.debug(
        f"GET Request: Athletes (includeInactive = {includeInactive})"
    )
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(
            f"Error {response.status_code}: {response.reason}"
        )

    data = response.json()['data']
    df = pd.json_normalize(data, meta=['count'], errors='ignore')
    df.attrs['Count'] = int(len(df.index))
    logger.info(
        f"Request successful. Athletes returned: {len(df.index)}"
    )
    return df
