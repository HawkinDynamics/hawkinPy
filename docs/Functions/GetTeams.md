__`GetTeams()`__

### Description
Get teams for an account. This function is designed to retrieve all teams within your organization.

### Returns
A Pandas DataFrame containing the teams' information, with columns:

* __id__: Team unique identifier.
* __name__: Team given name.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import GetTeams

# Get all teams
teams = GetTeams()
# Print teams table
print(teams)
```

_output_

| id                   | name               |
|----------------------|--------------------|
| KBHev5JXD9YY1Xz5zmSp | Test Team 1         |
| vW9iEKafhs2PamfKSdGC | Test Team 2         |
| yxYfkCEubB5o8xrLy5n2 | Test Team 3         |