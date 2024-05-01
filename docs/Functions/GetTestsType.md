__`GetTestsType(typeId: str, from_: int = None, to_: int = None, sync: bool = False, active: bool = True)`__

### Description
Get test trials only from a specific type of test. Allows filtering of results based on time frames, synchronization needs, and the active status of tests.

The typeId has been created to be more user friendly, as it accepts any of canonical Id, test type name, or common abbreviation:

| id | name | abbreviation |
| -- | ---- | ------------ |
| 7nNduHeM5zETPjHxvm7s | Countermovement Jump | CMJ |
| QEG7m7DhYsD6BrcQ8pic | Squat Jump | SJ |
| 2uS5XD5kXmWgIZ5HhQ3A |Isometric Test | ISO |
| gyBETpRXpdr63Ab2E0V8 | Drop Jump | DJ |
| 5pRSUQVSJVnxijpPMck3 | Free Run | FREE |
| pqgf2TPUOQOQs6r0HQWb | CMJ Rebound | CMJR |
| r4fhrkPdYlLxYQxEeM78 | Multi Rebound | MR |
| ubeWMPN1lJFbuQbAM97s | Weigh In | WI |
| rKgI4y3ItTAzUekTUpvR | Drop Landing | DL |

### Parameters
__`typeId`__: _(str)_ The canonical test ID, test type name, or test name abbreviation. Must correspond to known test types.

__`from_`__: _(int)_ Unix timestamp specifying the start time from which tests should be fetched. Default is None, which fetches tests from the beginning.
    
__`to_`__: _(int)_ Unix timestamp specifying the end time until which tests should be fetched. Default is None, which fetches tests up to the current time.

__`sync`__: _(bool)_ If True, the function fetches updated and newly created tests to synchronize with the database. Default is False.

__`active`__: _(bool)_ If True, only active tests are fetched. If False, all tests including inactive ones are fetched. Default is True.

### Returns
A Pandas DataFrame containing details of the test trial, with columns:

* __id__: Unique test id
* __timestamp__: Unix timestamp of the the recording time of the trial.
* __athlete_data__: Columns of athlete data. Same as DataFrame returned from GetAthletes(.id, .name, .teams, .groups, .active, extranal.name)
* __testType_data__: Columns of test type data(.id, .name, .canonicalId, .groups, .active, extranal.name)
* __tags_data__: Columns of test tags data(.id, .name). Each is a list of any applicable values.
* __all test metrics__: Calculated center of mass displacement from starting height at each time point.

DataFrame is also returned with specific attributes:

* __Canonical Id__
* __Test Type Name__
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

``` Python title=" Get Test Type Specific Test Data"
from hdforce import GetTestsType

# Get CMJ test data
Data = GetTestsType(typeId = "CMJ", from_ = 1690859091, to_ = 1711392994)

# Print DataFrame Attibutes
print(f"Canonical Id: {Data.attrs["Canonical Id"]}")
print(f"Test Type Name: {Data.attrs["Test Type Name"]}")
print(f"Count: {Data.attrs["Count"]}")
print(f"Last Sync:{Data.attrs["Last Sync"]}")
print(f"Last Test Time: {Data.attrs["Last Test Time"]}")

# Print rows 0:3
print(Data.iloc[:3, :20]) # All columns not printed
```

``` txt title="Print Outputs"
Canonical Id:7nNduHeM5zETPjHxvm7s
Test Type Name: Countermovement Jump
Count: 58
Last Sync: 1711392834
Last Test Time: 1711392822
```

_DataFrame output_

| id | timestamp | athlete_id | athlete_name | athlete_teams | athlete_groups | athlete_active | external_GradYear | external_location | external_uniqueId | external_StudentID | external_DPMb6ek2mgUNVcg8siSqpnIvE2i2 | testType_id | testType_name | testType_canonicalId | tag_ids | tag_names | segment | Right Avg_ Propulsive Force(N) | Relative Propulsive Net Impulse(N_s/kg) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5BgdD9160h7cC5Bc6Jj4 | 1698115161 | OLbsebtmf81eiwg1AeE5 | Lauren Green | ['DPMb6ek2mgUNVcg8siSqpnIvE2i2', 'vW9iEKafhs2PamfKSdGC'] | ['yh8RnOvg56dQNrZGBKWZ'] | True | 2004 | Whittier | 83keo9wjei939ekd9 | SA0042643 | nan | 96baa7ef1443c7a219702eb22e3e68d3 | Countermovement Jump | 7nNduHeM5zETPjHxvm7s | [] | [] | Countermovement Jump:2 | 1164.0342 | 2.8705 |
| SXxI8eNgN2qha7aAQ6tJ | 1698115180 | OLbsebtmf81eiwg1AeE5 | Lauren Green | ['DPMb6ek2mgUNVcg8siSqpnIvE2i2', 'vW9iEKafhs2PamfKSdGC'] | ['yh8RnOvg56dQNrZGBKWZ'] | True | 2004 | Whittier | 83keo9wjei939ekd9 | SA0042643 | nan | 96baa7ef1443c7a219702eb22e3e68d3 | Countermovement Jump | 7nNduHeM5zETPjHxvm7s | [] | [] | Countermovement Jump:3 | 1118.2702 | 2.8758 |
| AFv5YgN7yQimpZHSOQJE | 1698115201 | OLbsebtmf81eiwg1AeE5 | Lauren Green | ['DPMb6ek2mgUNVcg8siSqpnIvE2i2', 'vW9iEKafhs2PamfKSdGC'] | ['yh8RnOvg56dQNrZGBKWZ'] | True | 2004 | Whittier | 83keo9wjei939ekd9 | SA0042643 | nan | 96baa7ef1443c7a219702eb22e3e68d3 | Countermovement Jump | 7nNduHeM5zETPjHxvm7s | [] | [] | Countermovement Jump:4 | 1148.602 | 2.9366 |