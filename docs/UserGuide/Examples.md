### Log Configuration
Run at the beginning of script/session to set desired logging settings

```Python title="Log File for Debugging"
from hdforce import LogConfig

# Configure to set up a log file for thorough debugging
LogConfig(file = TRUE, level = 'debug')
```
### Authentication

**Initial Set Up**

First use in a new environment. Storing refresh token and region.

``` Python title="New Environment Configuration"
from hdforce import AuthManager

AuthManager(
    region = "Americas", 
    authMethod: "env", 
    refreshToken_name = "HD_REFRESH_TOKEN", 
    refreshToken = "YourRefreshTokenHere"
    )
```

**Initial Set Up with File**

First use in a new environment and using the "file" method. The .env file should be created before authenticating, and can already include variables and values. 

``` title="'.env' file in root folder"
HD_REFRESH_TOKEN=YourRefreshTokenHere
REGION=Americas
ACCESS_TOKEN=
TOKEN_EXPIRATION=
CLOUD_URL=
```

If you want to update the file variables
``` Python title="New Variables"
from hdforce import AuthManager

AuthManager(
    region = "Europe", 
    authMethod: "file", 
    refreshToken_name = "HD_REFRESH_TOKEN", 
    refreshToken = "YourRefreshTokenHere",
    env_file_name = ".env"
    )
```

### Create Useful Variables

``` Python title="Get HD and Org Data"
import hdforce as hd

# Get Test types and IDs
types = hd.GetTypes()

# Get all athletes (including inactive)
players = hd.GetAthletes( inactive = True)

# Get Teams, Groups, Tags for filtering tests
teams = hd.GetTeams()
groups = hd.GetGroups()
tags = hd.GetTags()
```

### Get Test Data

**Get Tests**
``` Python title="Get Tests of all types, athletes, teams, and groups"
from hdforce import GetTests

# Set from and to time points
time1 = 1690859091
time2 = 1711392994

# get all tests in system (not recommended)
allTests = GetTests()

# get test from a time
fromTests = GetTests(from_ = time2)

# get test up to a time
fromTests = GetTests(to_ = time1)

# get test from between time points
fromTests = GetTests(from_ = time1, to_ = time2)

# Sync tests since last sync (only new or updated tests)
lastSync = allTests.attrs["Last Sync"] # find last sync value in returned DataFrame attributes
newTests = GetTests(from_ = lastSync , sync = True)
```

**Get Tests by Athlete**
``` Python title="Get Tests of specific types, athletes, teams, and groups"
from hdforce import GetTestsAth, GetTestsType, GetTestsGroup, GetTestsTeam

# Set from and to time points
time1 = 1690859091
time2 = 1711392994

# get all tests for athlete
me = players.id[players["name"] == "Lauren Green"] # Get my athlete info from players variable

myId = me.iloc[0] # Get my id

myTests = GetTestsAth(athleteId = myId) # Get my tests
```

**Get Tests by Type**
``` Python title="Sync CMJ Tests Since Time2"
# get CMJ tests since time2
updateCMJ = GetTestsType(typeId = 'Countermovement Jump', from_ = time2, sync = True)
```

**Get Group Test Up to time 1**
```Python title="Group1 Tests up to Time1"
theGroup = groups.id[groups["name"] == "group1"]
groupTests = GetTestsGroup(groupId = theGroup, to_ = time1)
```

**Get Team Test from time2**
``` Python title="Teams 1,2,3 from time 2"
# Specify the team names you want to find indices for
team_names = ['Team 1', 'Team 3', 'Team 6']

# Get indices for the specified team names
indices = teams[teams['name'].isin(team_names)].index.tolist()

# Select the team IDs using iloc
teamIds = teams.iloc[indices]['id']

teamTests = GetTestsTeam(teamId = teamIds, from_ = time2)
```

**Get Force-Time Data**
``` Python title="My First Test Force-Time Data"
from hdforce import GetTestsAth, GetForceTime

# Get my athlete info from players variable
me = players.id[players["name"] == "Lauren Green"]

# Get my id
myId = me.iloc[0]

# Get my tests
myTests = GetTestsAth(athleteId = myId)

# Get test trial id of first test
someTest = myTests.iloc[0]

# Get force time data
ftData = GetForceTime(testId = someTest)
```