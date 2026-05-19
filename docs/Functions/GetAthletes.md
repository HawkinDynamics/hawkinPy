__`GetAthletes(includeInactive: bool = False)`__

### Description
Get the athletes for an account.

### Parameters
`includeInactive`: (_bool_) Specifies whether to include inactive athletes in the results. Default is False (inactive athletes are not included).

### Returns
A Pandas DataFrame containing the athletes' information, with columns:

* __id__: Athlete's unique identifier.
* __name__: Athlete's given full name.
* __teams__: A nested list of athlete's team ids as strings.
* __groups__: A nested list of athlete's group ids as strings.
* __active__: Boolean indicating if the athlete's profile is active (not archived).
* __image__ _(optional)_: URL to the athlete's photo. `None` when the photo has been explicitly cleared; column absent when no photo was ever uploaded.
* __position__ _(optional)_: Free-text playing position (e.g. "Forward", "Catcher").
* __dob__ _(optional)_: Date of birth as an ISO-8601 date string (`YYYY-MM-DD`).
* __sport__ _(optional)_: Free-text sport name.
* __height__ _(optional)_: Athlete height in **centimeters**, range `[1, 300]`.
* __lastTestedOn__ _(optional)_: Unix epoch milliseconds of the athlete's most recent test session.
* __external__: Columns dynamically created for each external attribute associated with the athletes. (example = external.ExternalId: value)

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

_Default: inactive = False_
``` Python
from hdforce import GetAthletes

# returns all athletes, including inactive
players = GetAthletes(includeInactive = True)
# Find Lauren Green
lg = players[players["name"] == "Lauren Green"]
# Print lg table
print(lg)
```

_output_

| id                   | name         | teams                                            | groups               | active | external.GradYear | external.location | external.uniqueId  | external.StudentID |
|----------------------|--------------|--------------------------------------------------|----------------------|--------|-------------------|-------------------|--------------------|--------------------|
| OLbsebtmf81eiwg1AeE5 | Lauren Green | ['DPMb6ek2mgUNVcg8siSqpnIvE2i2', 'vW9iEKafhs2PamfWQpFZ'] | ['yh8RnOvg56dQNrZGBKWZ'] | True   | 2004              | Whittier          | 83keo9wjei939ekd9  | SA0042643         |

