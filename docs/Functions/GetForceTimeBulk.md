__`GetForceTimeBulk(test_ids=None, export=False, export_dir=None, format="csv", file_naming=None, deidentify=False, **kwargs)`__

### Description
Fetch force-time data for **multiple** test trials in one call. Accepts an explicit list of test IDs or a DataFrame with an `id` column (e.g. the output of `GetTests()`); if neither is given, it delegates to `GetTests(**kwargs)` to resolve the targets. Results can be returned in memory or written to disk in several formats, with an accompanying metadata manifest.

### Parameters
__`test_ids`__: (_list[str] | pd.DataFrame | None_) A list of test IDs, or a DataFrame containing an `id` column. If `None`, `GetTests(**kwargs)` is called to determine the targets.

__`export`__: (_bool_) If `True`, write each test to a file in `export_dir`. Default `False` (return in memory).

__`export_dir`__: (_str_) Directory to write exported files to. Required when `export=True` (created if it does not exist).

__`format`__: (_str_) Export format: `"csv"`, `"tsv"`, `"json"`, or `"parquet"`. Default `"csv"`.

__`file_naming`__: (_list[str]_) Properties used to compose each output filename, joined by `_`. Options: `"test_id"`, `"athlete_name"`, `"athlete_id"`, `"testType_name"`, and `"date"`. Default `["test_id"]`.

__`deidentify`__: (_bool_) If `True`, replaces the athlete name with `"De-identified"` in the data attributes, the manifest, and any filename built from `athlete_name`.

__`**kwargs`__: Additional arguments forwarded to `GetTests()` when `test_ids` is `None` (e.g. `from_`, `to_`, `typeId`, `athleteId`).

### Returns
A Pandas DataFrame list or a list of file paths:

* If `export=False`: a `list[pd.DataFrame]`, one per test (each with the same attributes as `GetForceTime()`).
* If `export=True`: a `list[str]` of the files written. A `metadata_manifest.<format>` file is also written to `export_dir`, with one row per exported test (`filename`, `test_id`, `athlete_id`, `athlete_name`, `test_type`, `timestamp`, `date`).

### Raises
**Exception**

* No Access Token Found.

**Value Error**

* If `export=True` but `export_dir` is not provided.
* If `format` is not one of `csv`, `tsv`, `json`, `parquet`.
* If a DataFrame is passed without an `id` column.

### Example

``` Python title="Bulk force-time — in memory"
from hdforce import GetForceTimeBulk, GetTests

# From a query (delegates to GetTests)
frames = GetForceTimeBulk(typeId="CMJ", from_="2023-01-01")
print(len(frames), "tests returned")

# From the output of GetTests
tests = GetTests(from_="2023-01-01")
frames = GetForceTimeBulk(test_ids=tests.head(10))
```

``` Python title="Bulk force-time — export to disk"
# Export to CSV with athlete + test id filenames, de-identified
files = GetForceTimeBulk(
    test_ids=tests,
    export=True,
    export_dir="exports/forcetime",
    format="csv",
    file_naming=["athlete_name", "test_id"],
    deidentify=True,
)
# -> exports/forcetime/De_identified_<id>.csv, ...
#    exports/forcetime/metadata_manifest.csv
```
