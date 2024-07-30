# Getting Data

### Hawkin Specific data
While the purpose of the package is to help with accessing data specific to your organization, it may be helpful to store some data that is specific to Hawkin and the Hawkin Dynamics system. Things like test types and test metrics will help you call your data more efficiently and better understand the values you are seeing.

* `GetTypes` - Get the test type names and IDs for all the test types in the system. The response will be a data frame containing the tests that are in the HD system.
* `GetMetrics` - Get all the metrics for each test type. The response will be a data frame containing the test canonical ID, test type name, metric ID, metric label, a metric unit of measure, and description.

### Organization Specific Data

Every organization has data specific to them. With that, these entities will have unique IDs. It is important to have these IDs available to make the most of your test calls.

* `GetAthletes()` - Get the athletes for an account. Inactive players will only be included if `includeInactive` parameter is set to TRUE. The response will be a data frame containing the athletes that match this query.
* `GetTeams()` - Get the team names and IDs for all the teams in the org. The response will be a data frame containing the teams that are in the organization.
* `GetGroups()` - Get the group names and IDs for all the groups in the org. The response will be a data frame containing the groups that are in the organization.
* `GetTags()` - Get the tag names, IDs, and descriptions for tags created by users in your org. The response will be a data frame.

### Get Test Data

This is what you are here for. These functions allow you to call test data most efficiently. It is encouraged that you take advantage of the `from_`, `to_`, and `sync` parameters. This will help prevent from having calls with large payloads that may timeout and fail.

#### Get Test Arguments

* `from_` =  Optionally supply a time (Unix timestamp) you want the tests from. If you do not supply this
value you will receive every test. This parameter is best suited for bulk exports of historical data.
* `to_` = Optionally supply a time (Unix timestamp) you want the tests to. If you do not supply this value
you will receive every test from the beginning of time or the optionally supplied `from_`
parameter. This parameter is best suited for bulk exports of historical data
* `sync` = The result set will include updated and newly created tests, following the time constraints of `from_` and `to_`. This parameter is best suited to keep your database in sync with the Hawkin database. It cannot and should not be used to fetch your entire database. A recommended strategy would be to have a job that runs on a short interval e.g. every five minutes that sends the `lastSyncTime` that it received as the `from_` parameter with `sync=True`.
* `includeInactive` = Default to False, where only active tests are returned. If True, all tests including inactive ones are returned.

#### Get Test Function

> As of July 10, 2024, `GetTestsAth`, `GetTestsType`, `GetTestsTeam`, and `GetTestsGroup` 
> have been deprecated for the preferred use of `GetTests`. This function will be fully 
> superseded Jan 01, 2025 12:00:00.

* `GetTests()` - The primary function to call tests is `get_tests`. This is a base request for tests that, as of 2024-07-10, accepts all arguments : 'from', 'to', 'sync', 'includeInactive', 'athleteId', 'testTypeId', 'teamId', and 'groupId'. Using this function, you have complete control of the tests being requested from the cloud. It is important to understand that requests can **NOT** include any combination of 'athleteId', 'testTypeId', 'teamId', or 'groupId'. This will result in and error. Any of these arguments **CAN** be used with 'from', 'to', 'active', and 'sync'.
* `GetTestsAth()` - Get only tests of the specified athlete from your organization. You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from the athlete, within the time range (if specified).
* `GetTestsType()` - Get only tests of the specified test type from your organization. You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from that test type, within the time range (if specified).
* `GetTestsTeam()` - Get only tests of the specified teams from your organization. Requires a `teamId` argument, which expects a text string, list or tuple (max of 10 teams). You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from those teams, within the time range (if specified).
* `GetTestsGroup()` - Get only tests of the specified groups from your organization. Requires a `groupId` argument, which expects a text string, list or tuple (max of 10 groups). You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from those groups, within the time range (if specified).
* `GetForceTime()` - Get the force-time data for a specific test by id. This includes both left, right and combined force data at 1000hz (per millisecond). Calculated velocity, displacement, and power at each time interval will also be included.
