__`GetTypes()`__

### Description
Gets the test type names and IDs from Hawkin Dynamics System. These are foundational and static.

### Returns
A Pandas DataFrame containing the test type information, with columns:

* __id__: Test type unique identifier (Canonical Id).
* __name__: Test type common name.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import GetTypes

# Get test types
testTypes = GetTypes()
# Print type table
print(testTypes)
```

_output_

| id                   | name                 |
|----------------------|----------------------|
| 7nNduHeM5zETPjHxvm7s | Countermovement Jump |
| QEG7m7DhYsD6BrcQ8pic | Squat Jump           |
| 2uS5XD5kXmWgIZ5HhQ3A | Isometric Test       |
| gyBETpRXpdr63Ab2E0V8 | Drop Jump            |
| 5pRSUQVSJVnxijpPMck3 | Free Run             |
| pqgf2TPUOQOQs6r0HQWb | CMJ Rebound          |
| r4fhrkPdYlLxYQxEeM78 | Multi Rebound        |
| ubeWMPN1lJFbuQbAM97s | Weigh In             |
| rKgI4y3ItTAzUekTUpvR | Drop Landing         |
| 4KlQgKmBxbOY6uKTLDFL | TS Free Run          |
| umnEZPgi6zaxuw0KhUpM | TS Isometric Test    |
