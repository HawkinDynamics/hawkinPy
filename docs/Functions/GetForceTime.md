__`GetForceTime(testId: str)`__

### Description
Get force-time data for an individual test trial from an account.

### Parameters
__`testId`__: (_str_) The unique ID given to each test trial.

### Returns
A Pandas DataFrame containing details of the test trial, with columns:

* __Time (s)__: Time elapsed in seconds.
* __LeftForce (N)__: Force at time point from left plate.
* __RightForce (N)__: Force at time point from right plate.
* __CombinedForce (N)__: Combined force (Left + Right) at each time point.
* __Velocity (m/s)__: Calculated center of mass velocity at each time point.
* __Displacement (m)__: Calculated center of mass displacement from starting height at each time point.
* __Power (W)__: Calculated power of mass at each time point.
* __RSI__: Calculated Reactive Strength Index (if applicable).


### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.

**Value Error**

* If the 'testId' parameter is not a string.

### Example

``` Python title=" Get Tests Force-Time Data"
from hdforce import GetForceTime

# Get force time data
ftData = GetForceTime(testId = someTest)
# Print rows 2000:2005
print(ftData.iloc[2000:2005])
```

_output_

| Index | Time(s) | LeftForce(N) | RightForce(N) | CombinedForce(N) | Velocity(m/s) | Displacement(m) | Power(W)    | rsi |
|-------|---------|--------------|---------------|------------------|---------------|-----------------|-------------|-----|
| 2000  | 2.001   | 42           | 119           | 161              | -1.119636     | -0.077419       | -180.261446 | []  |
| 2001  | 2.002   | 46           | 122           | 168              | -1.128090     | -0.078543       | -189.519185 | []  |
| 2002  | 2.003   | 49           | 126           | 175              | -1.136487     | -0.079675       | -198.885184 | []  |
| 2003  | 2.004   | 53           | 130           | 183              | -1.144821     | -0.080816       | -209.502302 | []  |
| 2004  | 2.005   | 56           | 135           | 191              | -1.153090     | -0.081965       | -220.240178 | []  |