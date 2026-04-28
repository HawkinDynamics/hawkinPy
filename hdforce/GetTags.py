# Dependencies -----
import requests
import os
import pandas as pd
# Package imports
from .utils import logger, ensure_token

# -------------------- #
# Get Tags -----


def GetTags() -> pd.DataFrame:
    """Get tag names, IDs, and descriptions for an account.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns: id, name, description.

    Raises
    ------
    Exception
        If the HTTP response status is not 200.
    """
    a_token = ensure_token()
    url = f"{os.getenv('CLOUD_URL')}/tags"

    logger.debug("GET Request: Tags")
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(
            f"Error {response.status_code}: {response.reason}"
        )

    data = response.json()
    df = pd.json_normalize(
        data['data'], meta=['count'], errors='ignore'
    )
    df.attrs['Count'] = int(len(df.index))
    logger.info(f"Request successful. Tags returned: {len(df.index)}")
    return df
