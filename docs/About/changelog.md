# Changelogs

## hdforce v2.2.0

### New Features
* `NewAthlete` gains optional `position`, `sport`, `dob` and `height`, and `CreateAthletes()` / `UpdateAthletes()` now send all four as native athlete fields (never inside `external`).
  * `dob` accepts a `datetime.date`, a 4-digit year (int or str) or `"YYYY-MM-DD"`, and is sent as `"YYYY-MM-DD"` or `"YYYY"`. An invalid format or impossible date raises a `ValidationError`.
  * `height` is in centimeters and rounded to 1 decimal place. Sending a height below 100 emits a `UserWarning`, because the API reads those values back as legacy feet/inches (95 reads back as 241.3).
  * Fields left as `None` (or blank) are not sent: on create they stay unset, on update they stay unchanged. The API can't clear these fields; clear them in the Hawkin app.
* Network-free unit tests (`tests/test_athlete_profile_fields.py`) cover the create/update payloads.

### Behaviour Changes
* `CreateAthletes()` and `UpdateAthletes()` no longer send fields whose value is `None`. Previously `Athlete.image=None` was sent as `null` on every update; it is now omitted, so the athlete's photo is left unchanged.
* `lastTestedOn` is read-only and is never sent.
* `external` handling is unchanged when you send it: it is sent as given and replaced, not merged, on update.

### Bug Fixes
* **`import hdforce` failed on a fresh install of 2.1.0** with `ModuleNotFoundError: No module named 'pandas.core.col'`. hdforce 2.1.0 allowed `pyjanitor` up to 0.32, and pyjanitor 0.32.x imports a pandas 3 module without declaring pandas 3 as a requirement, so pip paired it with the pandas 2 that hdforce requires. `pyjanitor` is now pinned to 0.30.x. If you are on 2.1.0, upgrade to 2.2.0, or run `pip install "pyjanitor<0.31"`.
* `UpdateAthletes()` now attributes each result by athlete `id` instead of by name. Two athletes in one batch can share a name, and keying on name collapsed their results: a failed update could be reported as successful, and a failure reason could land on the wrong athlete. A response entry that arrives without an `id` still falls back to the name.
* `UpdateAthletes()` now sends only the fields you set on each `Athlete`; every other field is left unchanged. Previously the `Athlete` defaults (`active=True`, `teams=[]`, `groups=[]`, `external={}`) were always sent, so a rename-only update such as `Athlete(id=..., name="New Name")` removed the athlete from all teams and groups, deleted all custom properties and re-activated an inactive athlete. A field you set explicitly is still sent even when it equals the default (e.g. `teams=[]` or `active=True`). `CreateAthletes()` is unchanged and still sends the `NewAthlete` defaults.

## hdforce v2.1.0

### New Features
* `GetTests()` gains three optional keyword arguments that map to the Hawkin API v1.16 response-shape query params: `useNulls` (default `True`), `rounding` (default `False`) and `nestMetrics` (default `False`). Only a non-default value is sent, so existing calls produce identical requests. They exist so customers migrating from a legacy named API endpoint to `/api/v1` can reproduce that endpoint's payload; new integrations should leave the defaults.
  * `useNulls=False` keeps the string `"N/A"` for non-calculable metrics instead of `NaN` (affected metric columns become object dtype).
  * `rounding=True` returns each metric rounded to its standard display precision. Inert when `nestMetrics=True`.
  * `nestMetrics=True` returns a long DataFrame — one row per test × metric with `metric_id`, `metric_label`, `metric_units` and `metric_value` columns beside the trial, athlete and test-type columns. A test with no numeric metrics keeps a single row with `NaN` metric fields.
* Network-free unit tests (`tests/test_response_shapes.py`) cover query-param emission and both response shapes.

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