# HDFORCE v1.2.0 <img src="docs/img/hdlogo_sm.png" align="right" alt="" width="120" />


**Get your data from the Hawkin Dynamics API**

<!-- badges: start -->
![GitHub Release](https://img.shields.io/github/v/release/HawkinDynamics/hawkinPy)
[![Test Py Versions and OS](https://github.com/HawkinDynamics/hawkinPy/actions/workflows/push-test.yml/badge.svg?branch=main)](https://github.com/HawkinDynamics/hawkinPy/actions/workflows/push-test.yml)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/HawkinDynamics/hawkinPy/main)
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![lifecycle](https://img.shields.io/badge/lifecycle-stable-green.svg)](https://www.tidyverse.org/lifecycle/#stable)
[![license](https://img.shields.io/badge/license-MIT%20+%20file%20LICENSE-lightgrey.svg)](https://choosealicense.com/)
<!-- badges: end -->

## How To Use The HDFORCE Package

HDFORCE provides simple functionality with Hawkin Dynamics API. These functions are for use with ‘Hawkin Dynamics Beta API’ version 1.10-beta. You must be a Hawkin Dynamics user with an active integration account to utilize functions within the package.

## Functions
This API is designed to get data out of your Hawkin Dynamics server and interact with your data more intimately. It is not designed to be accessed from client applications directly. There is a limit on the amount of data that can be returned in a single request (256 MB). As your database grows, it will be necessary to use the `from_` and `to_` parameters to limit the size of the responses. Responses that exceed the memory limit will timeout and fail. It is advised that you design your client to handle this from the beginning. A recommended pattern would be to have two methods of fetching data. A scheduled pull that uses the `from_` and `to_` parameters to constrain the returned data to only tests that have occurred since the last fetch e.g. every day or every 5 minutes. And then a pull that fetches the entire database since you began testing that is only executed when necessary. A recommended way of doing this is to generate the `from_` and `to_` parameters for each month since you started and send a request for each either in parallel or sequentially.

This package was meant to help execute requests to the Hawkin Dynamics API with a single line of code. There are 13 functions to help execute 4 primary objectives:

### Authentication
Use the Refresh Token generated by https://cloud.hawkindynamics.com/integrations to get a valid Access Token. Only the organization administrator account can generate API tokens. Use this function to initiate access to your data in the cloud. All other HDFORCE functions will depend on the values returned from this function.

In HDFORCE, we can create and manage your authentication settings with the `authManager` function. The arguments passed will be used to handle authentication for the other functions used in the program. With this function, you can control these settings:

* __region__: Sets the URL prefix of your cloud site.
* __authMethod__: Sets storage method of auth variables. One of env, file, or manual. Default to 'env'.
* __refreshToken_name__: Provide or set the name of the refresh Token variable. Default to "HD_REFRESH_TOKEN".
* __refreshToken__: Optionally provided to pass a token for authentication when authMethod="manual". Else it will set the refresh token value when provided.
* __env_file_name__: Required when authManager="file". Directs storage location of variables.

The authentication manager allows the user to manage authentication with various development strategies. The 'env' method was designed to allow for simple authentication while developing in a local or contained environment, where the refresh token and variables are stored in the system environment. The 'file' method can be used for more visible and dynamic interaction with the auth variables, as the refresh token and variables are stored with a .env file. While the 'manual' method allows for the use of the package without storing sensitive data, in so the refresh token is not stored and is only used for authentication. This could be helpful in the scenario of developing a password-protected application where the token can be used as a password.

In the case of the "file" method, the user will need to save a .env file in the source directory. When using this method, you will also need to pass the file name to the `env_file_name` argument as a string. It's most common to use something as simple as ".env", but you can name your file anything ending with .env.

Below is an example of what the .env file can look like. This can be used as a template, as the variable name "HD_REFRESH_TOKEN" is the default to what the `authManager` function will use for the `refreshToken_name`. If you want to use a different variable name, simply pass the string through the `refreshToken_name` argument, along with the token to the `refreshToken` argument. The other values for ACCESS_TOKEN, TOKEN_EXPIRATION, and CLOUD_URL are defaults within the `authManager` function and should be maintained.

``` PowerShell
# Inside your .env file

HD_REFRESH_TOKEN=your_api_token     # Replace With Your Refresh Token
REGION=your_region                  # Replace With Your URL region
ACCESS_TOKEN=                       # Access token will be stored here
TOKEN_EXPIRATION=                   # Token Expiration will be stored here
CLOUD_URL=                          # Your region's URL here
```

With the variables stored, we can use them with our other functions without worrying about authentication for each call.

``` Python
# Run authentication manager
AuthManager(authMethod="env", region= "Americas")

# Run authentication manager with file method
AuthManager(authMethod="file", env_file_name=".env", region= "Americas")

# Run authentication manager with manual method
AuthManager(authMethod="manual", region="Americas", refreshToken="your_refresh_token")

```

### Hawkin Specific data
While the purpose of the package is to help with accessing data specific to your organization, it may be helpful to store some data that is specific to Hawkin and the Hawkin Dynamics system. Things like test types and test metrics will help you call your data more efficiently and better understand the values you are seeing.

* `GetTypes` - Get the test type names and IDs for all the test types in the system. The response will be a data frame containing the tests that are in the HD system.
* `GetMetrics` - Get all the metrics for each test type. The response will be a data frame containing the test canonical ID, test type name, metric ID, metric label, a metric unit of measure, and description.

### Organization Specific Data
Every organization has data specific to them. With that, these entities will have unique IDs. It is important to have these IDs available to make the most of your test calls.

* `GetAthletes()` - Get the athletes for an account. Inactive players will only be included if `inactive` = True. The response will be a data frame containing the athletes that match this query.
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
* `active` = If True, only active tests are fetched. If False, all tests including inactive ones are fetched. The default is set to True.

#### Get Test Function
* `GetTests()` - Get the tests for your account. You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). The Response will be a data frame containing the trials within the time range (if specified).
* `GetTestsAth()` - Get only tests of the specified athlete from your organization. You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from the athlete, within the time range (if specified).
* `GetTestsType()` - Get only tests of the specified test type from your organization. You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from that test type, within the time range (if specified).
* `GetTestsTeam()` - Get only tests of the specified teams from your organization. Requires a `teamId` argument, which expects a text string, list or tuple (max of 10 teams). You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from those teams, within the time range (if specified).
* `GetTestsGroup()` - Get only tests of the specified groups from your organization. Requires a `groupId` argument, which expects a text string, list or tuple (max of 10 groups). You can specify a time frame `from_`, or `to_`, which the tests should come (or be synced). Response will be a data frame containing the trials from those groups, within the time range (if specified).
* `GetForceTime()` - Get the force-time data for a specific test by id. This includes both left, right and combined force data at 1000hz (per millisecond). Calculated velocity, displacement, and power at each time interval will also be included.

## Examples
This is a basic example that shows a common workflow:

### Authenticate Session
``` Python
# Dependencies
import hdforce
# Run authentication manager
AuthManager(authMethod="env", region= "Americas")
```
### Get HD Data
#### Test Types
``` Python
# Test Types
types = hdforce.GetTypes()

types
```

### Organization Data
#### Get Athletes
``` Python
# Get Athletes
roster = hdforce.GetAthletes( inactive= False) # inactive is default to False

# Athlete example
roster[roster['name'] =="Lauren Green"]
```

#### Get Tags
``` Python
# Get Tags
tags = hdforce.GetTags()

# Tags example
tags[0:6]
```

### Get Tests
``` Python
# Get Tags
allTests = hdforce.GetTests()
# Filter my tests
mytests = allTests[allTests['athlete.name'] =="Lauren Green"]
# Slice some rows and columns
df = mytests.iloc[:5,:15]

df
```