import pandas as pd
import datetime
import os
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.feather as feather
# Package imports
from .AuthManager import AuthManager
from .utils import ConfigManager
from .LoggerConfig import LoggerConfig
from .GetTests import GetTests

# Get a logger specific to this module
logger = LoggerConfig.get_logger(__name__)

# -------------------- #
# Build DB


def BuildDB(start_date, test_type="all", include_inactive=False, file_name="data", 
            file_type="csv", span=14):
    """
    Build a local database by downloading test data in increments over a specified range of days.
    
    Parameters:
    -----------
    start_date : str or int
        The starting date for data retrieval, as a 'YYYY-MM-DD' string or Unix timestamp.
    test_type : str, optional
        The type of test data to retrieve (default is "all").
    include_inactive : bool, optional
        Whether to include inactive tests in the download (default is False).
    file_name : str
        The name of the file to save the results.
    file_type : str
        The format to save the file ('csv', 'xlsx', 'parquet', 'feather').
    span : int, optional
        The number of days to download at a time (default is 14).
    """

    #----------------------------------------------------------------------------#
    # Check Token Access
    #----------------------------------------------------------------------------#

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

    #----------------------------------------------------------------------------#
    # Convert start_date to datetime object
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    elif isinstance(start_date, int):
        start_date = datetime.datetime.fromtimestamp(start_date)

    end_date = datetime.datetime.today()

    #----------------------------------------------------------------------------#
    # Initialize empty list to collect data
    data_frames = []
    last_sync_times = []

    #----------------------------------------------------------------------------#
    # Set test Type
    #----------------------------------------------------------------------------#

    # Evaluate for Test Type argument
    if test_type == "all":
        t_id = None
    else:
        # Check typeId
        type_ids = {
            "7nNduHeM5zETPjHxvm7s": ["7nNduHeM5zETPjHxvm7s", "Countermovement Jump", "CMJ"],
            "QEG7m7DhYsD6BrcQ8pic": ["QEG7m7DhYsD6BrcQ8pic", "Squat Jump", "SJ"],
            "2uS5XD5kXmWgIZ5HhQ3A": ["2uS5XD5kXmWgIZ5HhQ3A", "Isometric Test", "ISO"],
            "gyBETpRXpdr63Ab2E0V8": ["gyBETpRXpdr63Ab2E0V8", "Drop Jump", "DJ"],
            "5pRSUQVSJVnxijpPMck3": ["5pRSUQVSJVnxijpPMck3", "Free Run", "FREE"],
            "pqgf2TPUOQOQs6r0HQWb": ["pqgf2TPUOQOQs6r0HQWb", "CMJ Rebound", "CMJR"],
            "r4fhrkPdYlLxYQxEeM78": ["r4fhrkPdYlLxYQxEeM78", "Multi Rebound", "MR"],
            "ubeWMPN1lJFbuQbAM97s": ["ubeWMPN1lJFbuQbAM97s", "Weigh In", "WI"],
            "rKgI4y3ItTAzUekTUpvR": ["rKgI4y3ItTAzUekTUpvR", "Drop Landing", "DL"],
            "4KlQgKmBxbOY6uKTLDFL": ["4KlQgKmBxbOY6uKTLDFL", "TS Free Run", "TSFR"],
            "umnEZPgi6zaxuw0KhUpM": ["umnEZPgi6zaxuw0KhUpM", "TS Isometric Test", "TSISO"]
        }
        # Sort test type Id
        for key, values in type_ids.items():
            if test_type in values:
                t_id = key
                break
        else:
            logger.error("typeId incorrect. Check your entry")
            raise Exception("typeId incorrect. Check your entry")

    while start_date < end_date:
        # Calculate the to_date for this span
        to_date = start_date + datetime.timedelta(days=span)
        to_epoch_start = int(start_date.timestamp())
        to_epoch_end = int(min(to_date, end_date).timestamp())
        
        # Fetch test data from API
        logger.info(f"Fetching data from {start_date} to {to_date}")
        df = GetTests(from_=to_epoch_start, to_=to_epoch_end, typeId=t_id, includeInactive=include_inactive, sync= True)
        
        # Append to list of data frames and record Last Sync
        if isinstance(df, pd.DataFrame) and not df.empty:
            last_sync = df.attrs.get('Last Sync', None)
            if last_sync is not None:
                df['last_sync_time_attribute'] = last_sync  # Add as a column
            data_frames.append(df)
            last_sync_times.append(last_sync)
        
        # Update start_date for next iteration
        start_date = to_date

    #----------------------------------------------------------------------------#
    # Combine all data frames
    #----------------------------------------------------------------------------#
    if data_frames:
        full_data = pd.concat(data_frames, ignore_index=True)
        # Sort by 'timestamp' in descending order
        full_data = full_data.sort_values(by='timestamp', ascending=False)
    else:
        logger.warning("No data fetched.")
        return
    
    # Save the last sync times for all frames
    if last_sync_times:
        full_data.attrs['All Last Syncs'] = last_sync_times

    #----------------------------------------------------------------------------#
    # Save to file in specified format
    #----------------------------------------------------------------------------#
    if file_type == "csv":
        full_data.to_csv(f"{file_name}.csv", index=False)
    elif file_type == "xlsx":
        full_data.to_excel(f"{file_name}.xlsx", index=False)
    elif file_type == "parquet":
        table = pa.Table.from_pandas(full_data)
        pq.write_table(table, f"{file_name}.parquet")
    elif file_type == "feather":
        table = pa.Table.from_pandas(full_data)
        feather.write_feather(table, f"{file_name}.feather")
    else:
        logger.error("Unsupported file format specified.")
    
    logger.info(f"Data saved to {file_name}.{file_type}")

