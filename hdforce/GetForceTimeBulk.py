# Dependencies -----
import os
import re
import json
import pandas as pd
from typing import List, Optional, Union
# Package imports
from .utils import logger, ensure_token
from .GetForceTime import GetForceTime
from .GetTests import GetTests

# -------------------- #
# Get Force Time Bulk

# Map friendly file_naming keys -> GetForceTime DataFrame attrs
_NAME_ATTR_MAP = {
    "test_id": "Test ID",
    "athlete_name": "Athlete Name",
    "athlete_id": "Athlete ID",
    "testType_name": "Test Name",
    "test_name": "Test Name",
}


def _sanitize(value: str) -> str:
    """Make a string safe for use in a filename (alnum + underscores)."""
    safe = re.sub(r"[^A-Za-z0-9]", "_", str(value))
    safe = re.sub(r"_+", "_", safe)
    return safe.strip("_")


def _name_part(df: pd.DataFrame, prop: str) -> str:
    """Resolve one file_naming property into a sanitized string."""
    if prop in ("date", "test_date"):
        ts = df.attrs.get("Timestamp")
        if ts is not None:
            try:
                return ts.strftime("%Y%m%dT%H%M%S")
            except AttributeError:
                pass
        return "NA"
    attr = _NAME_ATTR_MAP.get(prop, prop)
    val = df.attrs.get(attr, "")
    if val is None or val == "":
        return "NA"
    return _sanitize(val)


def GetForceTimeBulk(
    test_ids: Optional[Union[List[str], pd.DataFrame]] = None,
    export: bool = False,
    export_dir: Optional[str] = None,
    format: str = "csv",
    file_naming: Optional[List[str]] = None,
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
        Export format: "csv", "tsv", "json", or "parquet". Default "csv".

    file_naming : list[str], optional
        Properties used to compose each output filename, joined by "_".
        Options: "test_id", "athlete_name", "athlete_id", "testType_name",
        and "date". Default ["test_id"].

    deidentify : bool, optional
        If True, replaces the athlete name with "De-identified" in both
        the data attributes and any filename/manifest entry.

    **kwargs
        Additional arguments passed to GetTests() when test_ids is
        None (e.g., from_, to_, typeId, athleteId).

    Returns
    -------
    list[pd.DataFrame] | list[str]
        If export=False: list of DataFrames (one per test).
        If export=True: list of file paths written (a
        ``metadata_manifest.<format>`` file is also written to
        export_dir).

    Raises
    ------
    ValueError
        If export=True but export_dir is not provided, if the format is
        unsupported, or if DataFrame input lacks an 'id' column.
    """
    ensure_token()

    if file_naming is None:
        file_naming = ["test_id"]

    # Resolve targets
    targets = test_ids

    if targets is not None and isinstance(targets, pd.DataFrame):
        if 'id' not in targets.columns:
            raise ValueError("DataFrame must contain an 'id' column.")
        targets = targets['id'].tolist()
        logger.info(f"Extracted {len(targets)} test IDs from DataFrame.")

    if targets is None:
        logger.info("Querying GetTests() for targets...")
        tests_df = GetTests(**kwargs)
        if tests_df.empty:
            logger.warning("No matching tests found.")
            return []
        targets = tests_df['id'].tolist()
        logger.info(f"Found {len(targets)} tests.")

    # Validate export settings
    valid_formats = ("csv", "tsv", "json", "parquet")
    if format not in valid_formats:
        raise ValueError(f"format must be one of {valid_formats}")

    if export:
        if export_dir is None:
            raise ValueError("export_dir is required when export=True.")
        os.makedirs(export_dir, exist_ok=True)

    sep = "\t" if format == "tsv" else ","

    # Process each test
    results = []
    saved_files = []
    manifest_rows = []

    for i, tid in enumerate(targets):
        try:
            df = GetForceTime(testId=tid)

            if deidentify:
                df.attrs['Athlete Name'] = "De-identified"

            if export:
                # --- Compose filename from file_naming ---
                parts = [_name_part(df, p) for p in file_naming]
                fname = f"{'_'.join(parts)}.{format}"
                fpath = os.path.join(export_dir, fname)

                # --- Manifest row ---
                ts = df.attrs.get("Timestamp")
                manifest_rows.append({
                    "filename": fname,
                    "test_id": df.attrs.get("Test ID"),
                    "athlete_id": df.attrs.get("Athlete ID"),
                    "athlete_name": df.attrs.get("Athlete Name"),
                    "test_type": df.attrs.get("Test Name"),
                    "timestamp": int(ts.timestamp()) if ts is not None else None,
                    "date": str(ts) if ts is not None else None,
                })

                # --- Write data file ---
                if format == "csv":
                    df.to_csv(fpath, index=False)
                elif format == "tsv":
                    df.to_csv(fpath, sep="\t", index=False)
                elif format == "parquet":
                    # pandas persists df.attrs (which holds a Timestamp) into
                    # the parquet metadata as JSON and fails to serialize it.
                    # The data file carries columns only; metadata lives in the
                    # manifest, so drop attrs before writing.
                    df_out = df.copy()
                    df_out.attrs = {}
                    df_out.to_parquet(fpath, index=False)
                elif format == "json":
                    payload = {
                        "metadata": {
                            "test_id": df.attrs.get("Test ID"),
                            "athlete_id": df.attrs.get("Athlete ID"),
                            "athlete_name": df.attrs.get("Athlete Name"),
                            "test_type": df.attrs.get("Test Name"),
                            "timestamp": str(ts) if ts is not None else None,
                        },
                        "samples": df.to_dict(orient="records"),
                    }
                    with open(fpath, "w") as f:
                        json.dump(payload, f, indent=2, default=str)

                saved_files.append(fpath)
            else:
                results.append(df)

            logger.debug(f"[{i + 1}/{len(targets)}] Processed: {tid}")

        except Exception as e:
            logger.error(f"Failed to process test {tid}: {e}")
            continue

    if export:
        # --- Write the metadata manifest ---
        if manifest_rows:
            manifest_df = pd.DataFrame(manifest_rows)
            mpath = os.path.join(export_dir, f"metadata_manifest.{format}")
            if format in ("csv", "tsv"):
                manifest_df.to_csv(mpath, sep=sep, index=False)
            elif format == "parquet":
                manifest_df.to_parquet(mpath, index=False)
            elif format == "json":
                manifest_df.to_json(mpath, orient="records", indent=2)
            saved_files.append(mpath)
            logger.info(
                f"Export complete. {len(saved_files)} files saved "
                f"to {export_dir} (incl. manifest)"
            )
        else:
            logger.warning("No files saved.")
        return saved_files
    else:
        logger.info(f"Returned {len(results)} force-time DataFrames.")
        return results
