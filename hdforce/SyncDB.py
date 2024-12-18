import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.feather as feather
import datetime
# Package imports
from .AuthManager import AuthManager
from .utils import ConfigManager
from .LoggerConfig import LoggerConfig
from .GetTests import GetTests

# Get a logger specific to this module
logger = LoggerConfig.get_logger(__name__)

# -------------------- #
# Sync DB

def SyncDB(file, include_inactive=False, new_file=None):
    """
    Sync Database with Latest Test Data
    
    Parameters:
    -----------
    file : str
        The path to the current database file. Supported file types include 'csv', 'xlsx', 'feather', and 'parquet'.
    include_inactive : bool, optional
        Whether to include inactive tests during sync (default is False).
    new_file : str, optional
        Provide a new file path to save the updated database. If None, overwrites the original file.
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
    # Read Original File
    #----------------------------------------------------------------------------#
    if file.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.endswith(".xlsx"):
        df = pd.concat(pd.read_excel(file, sheet_name=None), ignore_index=True)
    elif file.endswith(".feather"):
        df = pd.read_feather(path= file)
    elif file.endswith(".parquet"):
        df = pd.read_parquet(path= file) 
    else:
        logger.error("Unsupported file type")
        raise ValueError("Unsupported file type")

    logger.info(f"{len(df)} tests retrieved from {file}")

    #----------------------------------------------------------------------------#
    # Retrieve Last Sync Time
    #----------------------------------------------------------------------------#
    # Use the `last_sync_time_attribute` column if present; fallback to `last_sync_time`
    if 'last_sync_time_attribute' in df.columns:
        last_sync = df['last_sync_time_attribute'].max()
    elif 'last_sync_time' in df.columns:
        last_sync = df['last_sync_time'].max()
    else:
        logger.error("No valid last sync time column found in the file.")
        raise ValueError("The input file does not contain a valid last sync time column.")

    # Determine test type for new data fetch
    if df['testType_name'].nunique() > 1:
        type_check = None
        logger.info(f"Checking for new tests and updates since {datetime.datetime.fromtimestamp(last_sync)}")
    else:
        type_check = df['testType_name'].unique()[0].split("-")[0]
        logger.info(f"Checking for new {type_check} tests and updates since {datetime.datetime.fromtimestamp(last_sync)}")

    #----------------------------------------------------------------------------#
    # Fetch New Data
    #----------------------------------------------------------------------------#
    try:
        new_df = GetTests(from_=last_sync, sync=True, typeId=type_check, includeInactive=include_inactive)
    except Exception as err:
        logger.error(f"Error retrieving new tests: {err}")
        new_df = None

    #----------------------------------------------------------------------------#
    # Update DataFrame
    #----------------------------------------------------------------------------#
    if new_df is not None and not new_df.empty:
        # Update the `last_sync_time_attribute` column with the `Last Sync` attribute from `new_df`
        if 'Last Sync' in new_df.attrs:
            new_df['last_sync_time_attribute'] = new_df.attrs['Last Sync']

        # Identify matching IDs
        matching_ids = df['id'].isin(new_df['id'])
        df.loc[matching_ids, :] = new_df[new_df['id'].isin(df['id'])]

        # Add new cases
        new_ids = ~new_df['id'].isin(df['id'])
        df = pd.concat([df, new_df[new_ids]], ignore_index=True).sort_values(by='timestamp', ascending=False)

        logger.info(f"{len(new_df)} tests and updates since {datetime.datetime.fromtimestamp(last_sync)}")
    else:
        logger.info(f"No new tests or updates found since {datetime.datetime.fromtimestamp(last_sync)}")

    #----------------------------------------------------------------------------#
    # Save Updated File
    #----------------------------------------------------------------------------#
    if new_file is None:
        new_file = file

    if new_file.endswith(".csv"):
        df.to_csv(new_file, index=False)
    elif new_file.endswith(".xlsx"):
        df.to_excel(new_file, index=False)
    elif new_file.endswith(".feather"):
        feather.write_feather(df, new_file)
    elif new_file.endswith(".parquet"):
        table = pa.Table.from_pandas(df)
        pq.write_table(table, new_file)
    else:
        logger.error("Unsupported file type for saving")
        raise ValueError("Unsupported file type for saving")

    logger.info(f"Updated data saved to {new_file}")

