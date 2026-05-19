# Create function to call tests by type
import requests
import os
import pandas as pd
# Package imports
from .utils import responseHandler, logger, dtConverter, ensure_token

# -------------------- #
# Get All Tests


def GetTests(
    from_=None,
    to_=None,
    sync=False,
    athleteId=None,
    typeId=None,
    teamId=None,
    groupId=None,
    includeInactive=False,
    includeEid=False
) -> pd.DataFrame:
    """Get test trials using cursor-based pagination (API v1.13+).

    Fetches all matching test trials from the account. Uses server-side
    pagination (1,000 tests per page) and loops automatically until all
    pages are retrieved.

    Parameters
    ----------
    from_ : int | str, optional
        Unix timestamp (int) or date string ("YYYY-MM-DD") for the
        start of the time range.

    to_ : int | str, optional
        Unix timestamp (int) or date string ("YYYY-MM-DD") for the
        end of the time range.

    sync : bool, optional
        If True, uses syncFrom/syncTo for incremental sync.
        Default is False.

    athleteId : str, optional
        Filter by a single athlete ID.

    typeId : str, optional
        Canonical test ID, test type name, or abbreviation.

    teamId : str | list, optional
        Single team ID or list of team IDs (max 10).

    groupId : str | list, optional
        Single group ID or list of group IDs (max 10).

    includeInactive : bool, optional
        Default False. When False, sends includeInactive=false to the
        API so only active tests are returned server-side. Set True to
        include inactive (disabled) trials.

    includeEid : bool, optional
        Default False. When True, the API includes an `eid` (equipment ID)
        column on each test record identifying the hardware that produced
        the trial.

    Returns
    -------
    pd.DataFrame
        A DataFrame of test trials with attributes:
        - Last Sync: int (lastSyncTime from final page)
        - Last Test Time: int
        - Count: int (total tests across all pages)

    Raises
    ------
    Exception
        If the API returns a non-200 status code.
    ValueError
        If multiple filter parameters are provided simultaneously.
    """
    # Validate token
    a_token = ensure_token()

    # Create URL for request
    url = os.getenv("CLOUD_URL")

    # Build query parameters
    query = {}

    # Only one filter param allowed
    provided_params = [athleteId, typeId, teamId, groupId]
    provided_count = sum(1 for p in provided_params if p is not None)
    if provided_count > 1:
        raise ValueError(
            "Only one of athleteId, typeId, teamId, or groupId "
            "can be provided at the same time."
        )

    # Convert dates to epoch
    if from_ is not None:
        from_ = dtConverter(from_)
    if to_ is not None:
        to_ = dtConverter(to_)

    # Time parameters
    if sync is True:
        if from_ is not None:
            query['syncFrom'] = from_
        if to_ is not None:
            query['syncTo'] = to_
    else:
        if from_ is not None:
            query['from'] = from_
        if to_ is not None:
            query['to'] = to_

    # Filter parameters
    if athleteId is not None:
        query['athleteId'] = athleteId

    if typeId is not None:
        type_ids = {
            "7nNduHeM5zETPjHxvm7s": [
                "7nNduHeM5zETPjHxvm7s",
                "Countermovement Jump", "CMJ"
            ],
            "QEG7m7DhYsD6BrcQ8pic": [
                "QEG7m7DhYsD6BrcQ8pic",
                "Squat Jump", "SJ"
            ],
            "2uS5XD5kXmWgIZ5HhQ3A": [
                "2uS5XD5kXmWgIZ5HhQ3A",
                "Isometric Test", "ISO"
            ],
            "gyBETpRXpdr63Ab2E0V8": [
                "gyBETpRXpdr63Ab2E0V8",
                "Drop Jump", "DJ"
            ],
            "5pRSUQVSJVnxijpPMck3": [
                "5pRSUQVSJVnxijpPMck3",
                "Free Run", "FREE"
            ],
            "pqgf2TPUOQOQs6r0HQWb": [
                "pqgf2TPUOQOQs6r0HQWb",
                "CMJ Rebound", "CMJR"
            ],
            "r4fhrkPdYlLxYQxEeM78": [
                "r4fhrkPdYlLxYQxEeM78",
                "Multi Rebound", "MR"
            ],
            "ubeWMPN1lJFbuQbAM97s": [
                "ubeWMPN1lJFbuQbAM97s",
                "Weigh In", "WI"
            ],
            "rKgI4y3ItTAzUekTUpvR": [
                "rKgI4y3ItTAzUekTUpvR",
                "Drop Landing", "DL"
            ],
            "4KlQgKmBxbOY6uKTLDFL": [
                "4KlQgKmBxbOY6uKTLDFL",
                "TS Free Run", "TSFR"
            ],
            "umnEZPgi6zaxuw0KhUpM": [
                "umnEZPgi6zaxuw0KhUpM",
                "TS Isometric Test", "TSISO"
            ]
        }
        t_id = None
        for key, values in type_ids.items():
            if typeId in values:
                t_id = key
                break
        if t_id is None:
            logger.error("typeId incorrect. Check your entry")
            raise ValueError("typeId incorrect. Check your entry")
        query['testTypeId'] = t_id

    if teamId is not None:
        if isinstance(teamId, (tuple, list)):
            query['teamId'] = ','.join(map(str, teamId))
        elif isinstance(teamId, str):
            query['teamId'] = teamId
        else:
            raise ValueError(
                "teamId must be a string or a list of strings."
            )

    if groupId is not None:
        if isinstance(groupId, (tuple, list)):
            query['groupId'] = ','.join(map(str, groupId))
        elif isinstance(groupId, str):
            query['groupId'] = groupId
        else:
            raise ValueError(
                "groupId must be a string or a list of strings."
            )

    # Server-side includeInactive (API v1.13+)
    if not includeInactive:
        query['includeInactive'] = 'false'

    # Optional: include equipment ID on each record
    if includeEid:
        query['includeEid'] = 'true'

    # Enable pagination
    query['paginate'] = 'true'

    # Pagination loop
    headers = {"Authorization": f"Bearer {a_token}"}
    all_pages = []
    last_sync_time = None
    last_test_time = None
    total_count = 0
    cursor = None

    logger.debug(f"Request URL: {url}")
    logger.debug(f"Query parameters: {query}")

    while True:
        # Refresh token if needed between pages
        a_token = ensure_token()
        headers = {"Authorization": f"Bearer {a_token}"}

        # Add cursor for subsequent pages
        current_query = dict(query)
        if cursor is not None:
            current_query['cursor'] = cursor

        response = requests.get(
            url, headers=headers, params=current_query
        )
        logger.debug(f"GetTests response code: {response.status_code}")

        if response.status_code != 200:
            logger.error(
                f"{response.status_code}: {response.reason}"
            )
            raise Exception(
                f"Error {response.status_code}: {response.reason}"
            )

        data = response.json()

        if data.get('count', 0) > 0:
            df_page = responseHandler(data)
            all_pages.append(df_page)

        # Capture envelope metadata from each page. The API may return
        # `lastSyncTime: null` / `lastTestTime: null` on empty pages, so
        # `or 0` covers both missing key and explicit null.
        last_sync_time = int(data.get('lastSyncTime') or 0)
        last_test_time = int(data.get('lastTestTime') or 0)
        total_count += data.get('count', 0) or 0

        # Check for more pages
        cursor = data.get('nextCursor')
        if cursor is None:
            break

        logger.debug("Page complete. Fetching next page...")

    # Combine all pages
    if len(all_pages) == 0:
        logger.info("No tests returned from query")
        return pd.DataFrame()

    df = pd.concat(all_pages, ignore_index=True)

    # Deduplicate
    df = df.drop_duplicates(subset=['id'], keep='first')

    # Set DataFrame attributes
    if typeId and t_id in type_ids:
        df.attrs['Type Id'] = t_id

    if teamId:
        df.attrs['Team Id'] = teamId
    if groupId:
        df.attrs['Group Id'] = groupId

    if athleteId:
        aName = df['athlete_name'].unique()
        if len(aName) > 0:
            df.attrs['Athlete Id'] = athleteId
            df.attrs['Athlete Name'] = str(aName[0])

    df.attrs['Last Sync'] = last_sync_time
    df.attrs['Last Test Time'] = last_test_time
    df.attrs['Count'] = total_count

    # Add last_sync_time column
    df['last_sync_time'] = last_sync_time

    logger.info(
        f"Request successful. {total_count} tests returned "
        f"across {len(all_pages)} pages."
    )
    return df
