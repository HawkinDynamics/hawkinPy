__`UpdateAthletes(athletes: List[Athlete])`__

### Description
Update athletes for your account. Up to 500 at one time.

### Parameters
`athletes`: (_list_) A list of Athletes with class of `Athlete`, which requires an "id" and "name" for each athlete entered. **Only the fields you set are sent; every field you don't set keeps its current value.** `Athlete(id="...", name="New Name")` renames the athlete without changing their active status, teams, groups or custom properties. "external" is the exception once you send it: it is replaced, not merged, so any custom property you leave out of it is removed.

### Classes
`Athlete`: (_class_) 
**REQUIRED**
* id: _str_
* name: _str_
*Optional* (left unchanged unless you set them)
* active: _bool_ Set `True` or `False` to change the athlete's status.
* teams: _list_ Replaces the athlete's teams. `teams=[]` removes them from all teams.
* groups: _list_ Replaces the athlete's groups. `groups=[]` removes them from all groups.
* external: _dict_ {externalName1 : externalValue1, externalName2 : externalValue2} Replaces all custom properties. `external={}` deletes them all.
* position: _str_ Free-text playing position (e.g. "Forward").
* sport: _str_ Free-text sport name (e.g. "Basketball").
* dob: _date_ | _int_ | _str_ Date of birth. Accepts a `datetime.date`, a 4-digit year (`1995` or `"1995"`) or `"YYYY-MM-DD"`. Sent as `"YYYY-MM-DD"` or `"YYYY"`. The API rejects years before 1900 or after the current year and full dates in the future; hdforce only checks the format.
* height: _float_ Height in **centimeters**, rounded to 1 decimal place. The API rejects values outside 0 to 300 (hdforce doesn't check the range); 0 counts as not provided and isn't sent.
* lastTestedOn: _int_ Read-only. Accepted so you can build an `Athlete` from `GetAthletes()` data, but never sent.

### Profile fields
`position`, `sport`, `dob` and `height` are sent as native athlete fields. They are never written into `external`.

* **Fields left as `None` (or blank) are not sent and stay unchanged.** The API can't clear these fields. To clear one, use the Hawkin app.
* **Height must be in centimeters.** The API reads any height below 100 back as a legacy feet/inches value (95 reads back as 241.3), so `UpdateAthletes()` emits a `UserWarning` when you send one. The request still goes ahead.
* `lastTestedOn` is never sent.
* `image` left as `None` is not sent, so the athlete's photo is unchanged.

### Returns
A list of AthleteResult objects indicating the success or failure of each athlete update.

* __AthleteResult__: Class with athlete name, id, success status, and reason. When the API rejects an athlete (for example an invalid `dob` or an out-of-range `height`), `successful` is `False` and `reason` holds the API's message.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.

**pydantic.ValidationError**

* If `dob` isn't a date, a 4-digit year or a real `"YYYY-MM-DD"` date, or `height` isn't a finite number.

### Example

``` Python
from hdforce import UpdateAthletes
from hdforce.Classes import Athlete

# Create list of athletes to update using the Athlete class
players = [
  Athlete(id= "N3wGuy$Un1q131D", name= "New Guy", active=False, external={"Title": "Younger Brother"},
          position="Forward", height=187.0),
  Athlete(id= "0ldGuy$Un1q131D", name= "Old Guy", active=False, external={"Title": "Older Brother"},
          dob="1998-02-14")
]

# Update players
updates = UpdateAthletes(athletes = players)

# Print Update Response
print(updates)
```

_output_

[
  AthleteResult(name='New Guy', successful=True, id='N3wGuy$Un1q131D', reason=[]),
  AthleteResult(name='Old Guy', successful=True, id='0ldGuy$Un1q131D', reason=[])
]
