__`GetGroups()`__

### Description
Get groups for an account. This function is designed to retrieve all groups within your organization.

### Returns
A Pandas DataFrame containing the groups' information, with columns:

* __id__: Team unique identifier.
* __name__: Team given name.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import GetGroups

# Get all groups
groups = GetGroups()
# Print groups table
print(groups)
```

_output_

| id                   | name               |
|----------------------|--------------------|
| KBHev5JXD9YY1Xz5zmSp | Test Group 1         |
| vW9iEKafhs2PamfKSdGC | Test Group 2         |
| yxYfkCEubB5o8xrLy5n2 | Test Group 3         |