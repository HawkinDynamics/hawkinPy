__`CreateAthletes(athletes: List[NewAthletes])`__

### Description
Create athletes for your account. Up to 500 at one time.

### Parameters
`athletes`: (_list_) A list of Athletes with class of `NewAthlete`, which requires a "name". If other parameters are left, they will assume default values.

### Classes
`NewAthlete`: (_class_) 
**REQUIRED**
* name: _str_
* active: _str_
*Optional*
* teams: _list_
* groups: _list_
* external: _dict_ {externalName1 : externalValue1, externalName2 : externalValue2}

### Returns
A list of AthleteResult objects indicating the success or failure of each athlete creation.

* __successful__: list of names of athletes added successfully
* __failures__: list of athletes that failed in execution, grouped by their reason for failure.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import CreateAthletes, NewAthlete

# Create list of athletes to add using NewAthlete class
players = [
  NewAthlete(name= "New Guy", active=False, teams=[], groups=[], external={"Title": "Younger Brother"}),
  NewAthlete(name= "Old Guy", active=False, teams=[], groups=[], external={"Title": "Older Brother"})
]

# Create players
newRoster = CreateAthletes(athletes = players)

# Print lgCreation Response
print(newRoster)
```

_output_

{
  "successful": ["New Guy", "Old Guy"],
  "failures": []
}

