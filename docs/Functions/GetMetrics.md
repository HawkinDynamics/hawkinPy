__`GetMetrics()`__

### Description
Gets the test metrics details from Hawkin Dynamics System.

### Returns
A Pandas DataFrame containing the information for the metrics of each test type, with columns:

* __canoniclaTestTypeId__: The unique identifier for each test type.
* __testTypeName__: The name of each metric.
* __id__: The unique identifier for each metric.
* __label__: The label (common name) for each metric
* __units__: Units of measure
* __description__: Full description of metric and calculation*


### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import GetMetrics

# Get all test metrics
metrics = GetMetrics()
# Print rows 10:15
print(metrics[10:15])
```

_output_

| canonicalTestTypeId | testTypeName        | id                        | label                          | units | description                                                                                                                                 |
|---------------------|---------------------|---------------------------|--------------------------------|-------|---------------------------------------------------------------------------------------------------------------------------------------------|
| 7nNduHeM5zETPjHxvm7s | Countermovement Jump | peakBrakingForce          | Peak Braking Force             | N     | The peak instantaneous vertical ground reaction force applied to the system center of mass during the braking phase.                       |
| 7nNduHeM5zETPjHxvm7s | Countermovement Jump | peakRelativeBrakingForce  | Peak Relative Braking Force    | %     | The peak instantaneous vertical ground reaction force applied to the system center of mass during the braking phase as a percentage of system weight. |
| 7nNduHeM5zETPjHxvm7s | Countermovement Jump | avgPropulsiveForce        | Avg. Propulsive Force          | N     | The average vertical ground reaction force applied to the system center of mass during the propulsion phase.                              |
| 7nNduHeM5zETPjHxvm7s | Countermovement Jump | avgRelativePropulsiveForce| Avg. Relative Propulsive Force | %     | The average vertical ground reaction force applied to the system center of mass during the propulsion phase as a percentage of system weight. |
| 7nNduHeM5zETPjHxvm7s | Countermovement Jump | peakPropulsiveForce       | Peak Propulsive Force          | N     | The peak instantaneous vertical ground reaction force applied to the system center of mass during the propulsion phase.                   |
