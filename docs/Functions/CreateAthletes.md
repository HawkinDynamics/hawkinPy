__`CreateAthletes(athletes: List[NewAthlete])`__

### Description
Create athletes for your account. Up to 500 at one time.

### Parameters
`athletes`: (_list_) A list of Athletes with class of `NewAthlete`, which requires a "name". If other parameters are left, they will assume default values.

### Classes
`NewAthlete`: (_class_) 
**REQUIRED**
* name: _str_
*Optional*
* active: _bool_ (default `True`)
* teams: _list_
* groups: _list_
* external: _dict_ {externalName1 : externalValue1, externalName2 : externalValue2}
* position: _str_ Free-text playing position (e.g. "Forward").
* sport: _str_ Free-text sport name (e.g. "Basketball").
* dob: _date_ | _int_ | _str_ Date of birth. Accepts a `datetime.date`, a 4-digit year (`1995` or `"1995"`) or `"YYYY-MM-DD"`. Sent as `"YYYY-MM-DD"` or `"YYYY"`. The API rejects years before 1900 or after the current year and full dates in the future; hdforce only checks the format.
* height: _float_ Height in **centimeters**, rounded to 1 decimal place. The API rejects values outside 0 to 300 (hdforce doesn't check the range); 0 counts as not provided and isn't sent.

### Profile fields
`position`, `sport`, `dob` and `height` are sent as native athlete fields. They are never written into `external`.

* Fields left as `None` (or blank) are not sent, and the athlete is created without them.
* **Height must be in centimeters.** The API reads any height below 100 back as a legacy feet/inches value (95 reads back as 241.3), so `CreateAthletes()` emits a `UserWarning` when you send one. The request still goes ahead.
* `lastTestedOn` is read-only and is never sent.

### Returns
A list of AthleteResult objects indicating the success or failure of each athlete creation.

* __AthleteResult__: Class with athlete name, id, success status, and reason. When the API rejects an athlete (for example an invalid `dob` or an out-of-range `height`), `successful` is `False` and `reason` holds the API's message.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.

**pydantic.ValidationError**

* If `dob` isn't a date, a 4-digit year or a real `"YYYY-MM-DD"` date, or `height` isn't a finite number.


### Example

``` Python
from datetime import date
from hdforce import CreateAthletes
from hdforce.Classes import NewAthlete

# Create list of athletes to add using NewAthlete class
players = [
  NewAthlete(name= "New Guy", active=False, external={"Title": "Younger Brother"},
             position="Guard", sport="Basketball", dob=date(2004, 6, 1), height=185.4),
  NewAthlete(name= "Old Guy", active=False, external={"Title": "Older Brother"},
             dob=1998)
]

# Create players
newRoster = CreateAthletes(athletes = players)

# Print Creation Response
print(newRoster)
```

_output_

[
  AthleteResult(name='New Guy', successful=True, id='N3wGuy$Un1q131D', reason=[]),
  AthleteResult(name='Old Guy', successful=True, id='0ldGuy$Un1q131D', reason=[])
]
