__`UpdateAthletes(athletes: List[Athletes])`__

### Description
Update athletes for your account. Up to 500 at one time.

### Parameters
`athletes`: (_list_) A list of Athletes with class of `Athlete`, which requires an "id", "name", and "active" for eah athlete entered. Any parameters omitted will retain their current values. Except for "external", which will be removed unless explicitly stated during update.

### Classes
`Athlete`: (_class_) 
**REQUIRED**
* id: _str_
* name: _str_
* active: _str_
*Optional*
* teams: _list_
* groups: _list_
* external: _dict_ {externalName1 : externalValue1, externalName2 : externalValue2}

### Returns
A list of AthleteResult objects indicating the success or failure of each athlete creation.

* __AthleteResult__: Class with athlete name, id, success status, and reason.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.

### Example

``` Python
from hdforce import UpdateAthletes, Athlete

# Create list of athletes to add using NewAthlete class
players = [
  Athlete(id= "N3wGuy$Un1q131D", name= "New Guy", active=False, external={"Title": "Younger Brother"}),
  Athlete(id= "0ldGuy$Un1q131D", name= "Old Guy", active=False, external={"Title": "Older Brother"})
]

# Create players
updates = UpdateAthletes(athletes = players)

# Print lgCreation Response
print(updates)
```

_output_

[
  AthleteResult(name= 'New Guy', id='N3wGuy$Un1q131D', successful=True, reason=None),
  AthleteResult(name= 'Old Guy', id='0ldGuy$Un1q131D', successful=True, reason=None)
]
