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
        A DataFrame with columns: id, name, teams, groups, active,
        and any external.* attribute columns.

    Raises
    ------
    Exception
        If the HTTP response status is not 200.
    """
    a_token = ensure_token()
    url_cloud = os.getenv("CLOUD_URL")
    url = f"{url_cloud}/athletes?inactive={includeInactive}"

    logger.debug(
        f"GET Request: Athletes (inactive = {includeInactive})"
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
