# Dependencies -----
import os
import pandas as pd
from typing import List, Optional, Union
# Package imports
from .utils import logger, ensure_token
from .GetForceTime import GetForceTime
from .GetTests import GetTests

# -------------------- #
# Get Force Time Bulk


def GetForceTimeBulk(
    test_ids: Optional[Union[List[str], pd.DataFrame]] = None,
    export: bool = False,
    export_dir: Optional[str] = None,
    format: str = "csv",
    deidentify: bool = False,
    **kwargs
) -> Union[List[pd.DataFrame], List[str]]:
    """Get force-time data for multiple tests in bulk.

    Parameters
    ----------
    test_ids : list[str] | pd.DataFrame | None, optional
        A list of test IDs, or a DataFrame with an 'id' column
        (e.g., output of GetTests()). If None, calls GetTests(**kwargs)
        to get test IDs.

    export : bool, optional
        If True, write data to files in export_dir. Default False.

    export_dir : str, optional
        Directory path for exported files. Required when export=True.

    format : str, optional
        Export format: "csv", "json", or "parquet". Default "csv".

    deidentify : bool, optional
        If True, replaces athlete name with "De-identified".

    **kwargs
        Additional arguments passed to GetTests() when test_ids is
        None (e.g., from_, to_, typeId, athleteId).

    Returns
    -------
    list[pd.DataFrame] | list[str]
        If export=False: list of DataFrames (one per test).
        If export=True: list of file paths written.

    Raises
    ------
    ValueError
        If export=True but export_dir is not provided, or if
        DataFrame input lacks an 'id' column.
    """
    ensure_token()

    # Resolve targets
    targets = test_ids

    if targets is not None and isinstance(targets, pd.DataFrame):
        if 'id' not in targets.columns:
            raise ValueError(
                "DataFrame must contain an 'id' column."
            )
        targets = targets['id'].tolist()
        logger.info(
            f"Extracted {len(targets)} test IDs from DataFrame."
        )

    if targets is None:
        logger.info("Querying GetTests() for targets...")
        tests_df = GetTests(**kwargs)
        if tests_df.empty:
            logger.warning("No matching tests found.")
            return []
        targets = tests_df['id'].tolist()
        logger.info(f"Found {len(targets)} tests.")

    # Validate export settings
    if export:
        if export_dir is None:
            raise ValueError(
                "export_dir is required when export=True."
            )
        os.makedirs(export_dir, exist_ok=True)

    valid_formats = ("csv", "json", "parquet")
    if format not in valid_formats:
        raise ValueError(
            f"format must be one of {valid_formats}"
        )

    # Process each test
    results = []
    saved_files = []

    for i, tid in enumerate(targets):
        try:
            df = GetForceTime(testId=tid)

            if deidentify:
                df.attrs['Athlete Name'] = "De-identified"

            if export:
                fname = f"{tid}.{format}"
                fpath = os.path.join(export_dir, fname)

                if format == "csv":
                    df.to_csv(fpath, index=False)
                elif format == "json":
                    df.to_json(fpath, orient="records", indent=2)
                elif format == "parquet":
                    df.to_parquet(fpath, index=False)

                saved_files.append(fpath)
            else:
                results.append(df)

            logger.debug(
                f"[{i + 1}/{len(targets)}] Processed: {tid}"
            )

        except Exception as e:
            logger.error(f"Failed to process test {tid}: {e}")
            continue

    if export:
        logger.info(
            f"Export complete. {len(saved_files)} files saved "
            f"to {export_dir}"
        )
        return saved_files
    else:
        logger.info(f"Returned {len(results)} force-time DataFrames.")
        return results
