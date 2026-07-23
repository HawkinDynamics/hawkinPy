# Changelogs

## hdforce v2.0.0

### Breaking Changes
* **Removed `GetTestsAth`, `GetTestsType`, `GetTestsTeam`, and `GetTestsGroup`.** These helpers were deprecated in v1.1.0 (2024) and have now been removed. Use `GetTests()` with the corresponding `athleteId`, `typeId`, `teamId`, or `groupId` argument instead. The internal `@deprecated` decorator (and its `functools`/`warnings` imports in `utils.py`) have also been removed since they are no longer used.
* `GetTests()` now uses cursor-based API pagination (API v1.13). All matching tests are fetched automatically across pages. Returns empty DataFrame instead of string when no data.
* `includeInactive` in `GetTests()` is now a server-side filter sent to the API. Client-side filtering removed.
* `CreateAthletes()` now returns `List[AthleteResult]` (was returning dict). Aligns with `UpdateAthletes()`.

### New Features
* `GetCOP()` — Fetch raw Center of Pressure (COP) time-series data for a test. Returns a DataFrame of the six COP series (`copX`, `copY`, `leftCopX`, `leftCopY`, `rightCopX`, `rightCopY`) keyed by `time`. Exclusive to the Free Run test type (other types return 404); COP values are `NaN` for samples with no weight on a plate.
* `GetForceTimeBulk()` — Fetch force-time data for multiple tests. Accepts a list of IDs or a DataFrame (e.g. `GetTests()` output), or delegates to `GetTests()`. Exports to csv/tsv/json/parquet with configurable `file_naming`, a `metadata_manifest.<format>` file, and de-identification (mirrors hawkinR's `get_forcetime_bulk()`).
* `CreateAthletes` and `UpdateAthletes` are now exported from the package (previously required direct import).

### Improvements
* Token refresh logic extracted to shared `ensure_token()` helper — eliminates 30+ lines of duplicated code across all functions.
* All API functions refactored for cleaner code and consistent error handling.

### Bug Fixes
* Fixed smoke_test.py calling `GetMetrics()` with invalid parameters.

## hdforce v1.1.2

* Bug fix: addition of new TruStrength test names and IDs to testTypeId validation method

## hdforce v1.1.1

* Corrected versioning and documentation

## hdforce v1.1.0

* Additions of CreateAthlete and UpdateAthlete functions
* Expansion of GetTests function to include 'team', 'group', type', and 'athlete' arguments
* Deprecation of GetTestsAth, GetTestsType, GetTestsTeam, and GetTestsGroup

## hdforce v1.0.01

* Initial release of production package
* Full logging configuration and Authentication features
* Tested on Python version 3.9 <-> 3.12, on Mac, Windows, and Linux

## hdforce v1.0.0rc0

* Improved logging
* bug fixes to GetTests functions
* Improved AuthMethods

## hdforce v0.0.0.1-beta

* Initial build for testing