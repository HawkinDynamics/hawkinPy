__`GetTags()`__

### Description
Get test tags for an account. This function is designed to retrieve all tags within your organization.

### Returns
A Pandas DataFrame containing the tags' information, with columns:

* __id__: Tag unique identifier.
* __name__: Tag given name.
* __description__: tag details

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import GetTags

# Get all teams
tags = GetTags()
# Print teams table
print(tags)
```

_output_

| id                  | name                  | description                            |
|---------------------|-----------------------|----------------------------------------|
| Afcw45lIkeHFnlUyDeSn | 10/5                  | 10/5 Multi-Rebound test protocol       |
| KmZmhxUqrbOhLLvRLAbG | 5/3                   | 5/3 Multi-Rebound test protocol        |
| Lgc8uJh80NacB8eaqjOg | 20kg                  | addition of 20kg load to system mass   |
| hVgWJkwHZ9Mm8XDymP3W | Hands On Hips         | Akimbo style jump                      |