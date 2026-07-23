# Dependencies -----
import requests
import pandas as pd
import os
# Package imports
from .utils import logger, ensure_token

# -------------------- #
# Get Center of Pressure


def GetCOP(testId: str) -> pd.DataFrame:
    """Get Center of Pressure (COP) data for an individual test trial.

    COP data is exclusive to the "Free Run" test type. Requesting any
    other test type returns a 404.

    Parameters
    ----------
    testId : str
        The unique ID of the test trial.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the COP time series, with columns:
        - time: Time elapsed in seconds (derived from the capture rate).
        - copX / copY: Combined center-of-pressure (mm from plate center).
        - leftCopX / leftCopY: Left plate COP.
        - rightCopX / rightCopY: Right plate COP.
        Individual COP values may be NaN for samples where no weight is on
        a given plate. DataFrame attributes include Test ID, Test Name,
        Athlete Name, Athlete ID, and Timestamp.

    Raises
    ------
    Exception
        If the HTTP response status is not 200.
    ValueError
        If testId is not a string, or no COP data is found (the test may
        not exist or may not be a Free Run test).
    """
    a_token = ensure_token()
    url_cloud = os.getenv("CLOUD_URL")

    if not isinstance(testId, str):
        logger.error("TestId must be a string")
        raise ValueError("TestId must be a string")

    url = f"{url_cloud}/cop/{testId}"

    logger.debug(f"GET COP data for test: {testId}")
    headers = {"Authorization": f"Bearer {a_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Error {response.status_code}: {response.reason}")
        raise Exception(
            f"Error {response.status_code}: {response.reason}"
        )

    data = response.json()
    # A team-scoped token not authorized for the test's teams gets a 200
    # with an empty body — treat as "no COP data".
    if not data or 'testType' not in data:
        logger.error(f"No COP data found for testId: {testId}")
        raise ValueError(
            f"No COP data found for testId '{testId}'. The test may not "
            f"exist or may not be a Free Run test."
        )

    def pad_array(arr, target_length, pad_value=None):
        return arr + [pad_value] * (target_length - len(arr))

    target_length = len(data.get("Time(s)", []))

    time_data = data.get("Time(s)", [])
    cop_x = pad_array(data.get("copX", []), target_length, None)
    cop_y = pad_array(data.get("copY", []), target_length, None)
    left_cop_x = pad_array(data.get("leftCopX", []), target_length, None)
    left_cop_y = pad_array(data.get("leftCopY", []), target_length, None)
    right_cop_x = pad_array(data.get("rightCopX", []), target_length, None)
    right_cop_y = pad_array(data.get("rightCopY", []), target_length, None)

    df = pd.DataFrame({
        "time": time_data,
        "copX": cop_x,
        "copY": cop_y,
        "leftCopX": left_cop_x,
        "leftCopY": left_cop_y,
        "rightCopX": right_cop_x,
        "rightCopY": right_cop_y
    })

    # Set attributes
    df.attrs['Test ID'] = data['id']
    df.attrs['Test Name'] = data['testType']['name']
    df.attrs['Athlete Name'] = data['athlete']['name']
    df.attrs['Athlete ID'] = data['athlete']['id']
    df.attrs['Timestamp'] = pd.to_datetime(
        data['timestamp'], unit='s'
    )

    logger.info(
        f"Request successful: {df.attrs['Test Name']} - "
        f"{df.attrs['Test ID']} - {df.attrs['Timestamp']}"
    )
    return df
