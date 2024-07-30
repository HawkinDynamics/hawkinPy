__`GetTestsTeam(teamId: str, from_: int = None, to_: int = None, sync: bool = False, includeInactive: bool = False)`__

> As of July 10, 2024 `GetTestsTeam` has been deprecated for the preferred use 
> of `GetTests`. This function will be fully superseded Jan 01, 2025 12:00:00.

### Description
Get test trials for specified team(s). Allows filtering of results based on time frames, synchronization needs, and the active status of tests.

### Parameters
__`teamId`__: _(str)_ A single team ID, tuple or list of team IDs to receive tests from specific teams.

__`from_`__: _(int)_ Unix timestamp specifying the start time from which tests should be fetched. Default is None, which fetches tests from the beginning.

__`to_`__: _(int)_ Unix timestamp specifying the end time until which tests should be fetched. Default is None, which fetches tests up to the current time.

__`sync`__: _(bool)_ If True, the function fetches updated and newly created tests to synchronize with the database. Default is False.

__`includeInactive`__: _(bool)_ Default to False, where only active tests are returned. If True, all tests including inactive ones are returned.

### Returns
A Pandas DataFrame containing details of the test trial, with columns:

* __id__: Unique test id
* __timestamp__: Unix timestamp of the the recording time of the trial.
* __athlete_data__: Columns of athlete data. Same as DataFrame returned from GetAthletes(.id, .name, .teams, .groups, .active, external.name)
* __testType_data__: Columns of test type data(.id, .name, .canonicalId, .groups, .active, external.name)
* __tags_data__: Columns of test tags data(.id, .name). Each is a list of any applicable values.
* __all test metrics__: Calculated center of mass displacement from starting height at each time point.

DataFrame is also returned with specific attributes:

* __Team Id__
* __Count__
* __Last Sync__
* __Last Test Time__


### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.

**Value Error**

* If there is an error in handling the JSON response or data formatting.

### Example

``` Python title=" Get Team Specific Test Data"
from hdforce import GetTestsTeam

# Get my team test data
Data = GetTestsTeam(teamId = ["teamId1", "teamId2", "teamId3"], from_ = 1690859091, to_ = 1711392994)

# Print DataFrame Attributes
print(f"Team IDs: {Data.attrs["Team Id"]}")
print(f"Count: {Data.attrs["Count"]}")
print(f"Last Sync:{Data.attrs["Last Sync"]}")
print(f"Last Test Time: {Data.attrs["Last Test Time"]}")

# Print rows 0:3
print(Data.iloc[:3, :20]) # All columns not printed
```

``` txt title="Print Outputs"
Team IDs: ["teamId1", "teamId2", "teamId3"]
Count: 58
Last Sync: 1711392834
Last Test Time: 1711392822
```

_DataFrame output_

| id | timestamp | athlete_id | athlete_name | athlete_teams | athlete_groups | athlete_active | external_GradYear | external_location | external_uniqueId | external_StudentID | external_DPMb6ek2mgUNVcg8siSqpnIvE2i2 | testType_id | testType_name | testType_canonicalId | tag_ids | tag_names | segment | Right Avg_ Propulsive Force(N) | Relative Propulsive Net Impulse(N_s/kg) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| YB35oOBAGHNQew0WziDt | 1690859091 | OLbsebtmf81eiwg1AeE5 | Lauren Green | ['teamId1', 'teamId2'] | ['yh8RnOvg56dQNrZGBKWZ'] | True | 2004 | Whittier | 83keo9wjei939ekd9 | SA0042643 | nan | 0f0017f87fb97445c95b9f2d1133b56b | Drop Landing | rKgI4y3ItTAzUekTUpvR | [] | [] | Drop Landing:3 | nan | nan |
| 2RnV4tM3J6IW2qYKgqg2 | 1690859127 | OLbsebtmf81eiwg1AeE5 | Lauren Green | ['teamId1', 'teamId3'] | ['yh8RnOvg56dQNrZGBKWZ'] | True | 2004 | Whittier | 83keo9wjei939ekd9 | SA0042643 | nan | 0f0017f87fb97445c95b9f2d1133b56b | Drop Landing | rKgI4y3ItTAzUekTUpvR | [] | [] | Drop Landing:4 | nan | nan |
| qNIZaBguZefAyar4oUtu | 1690859309 | OLbsebtmf81eiwg1AeE5 | Lauren Green | ['teamId2', 'teamId3'] | ['yh8RnOvg56dQNrZGBKWZ'] | True | 2004 | Whittier | 83keo9wjei939ekd9 | SA0042643 | nan | 7b22e645bdf341c90cf0f5459c957e6a | Drop Jump | gyBETpRXpdr63Ab2E0V8 | [] | [] | Drop Jump:3 | 1387.7479 | 1.5916 |