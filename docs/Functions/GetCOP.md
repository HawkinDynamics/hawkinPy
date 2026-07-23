__`GetCOP(testId: str)`__

### Description
Get Center of Pressure (COP) data for an individual test trial from an account.

COP data is exclusive to the __"Free Run"__ test type. Requesting any other test type returns a 404.

### Parameters
__`testId`__: (_str_) The unique ID given to each test trial.

### Returns
A Pandas DataFrame containing the COP time series of the test trial, with columns:

* __time__: Time elapsed in seconds (derived from the capture sampling rate).
* __copX__: Combined center-of-pressure, X axis (mm from plate center).
* __copY__: Combined center-of-pressure, Y axis.
* __leftCopX__: Left plate COP, X axis.
* __leftCopY__: Left plate COP, Y axis.
* __rightCopX__: Right plate COP, X axis.
* __rightCopY__: Right plate COP, Y axis.

Individual COP values may be `NaN` for samples where no weight is on a given plate (e.g. the left COP columns while the athlete is fully on the right plate). DataFrame attributes include Test ID, Test Name, Athlete Name, Athlete ID, and Timestamp.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.

**Value Error**

* If the 'testId' parameter is not a string.
* If no COP data is found (the test may not exist or may not be a Free Run test).

### Example

``` Python title=" Get Test Center-of-Pressure Data"
from hdforce import GetCOP

# Get COP data for a Free Run test
copData = GetCOP(testId = someFreeRunTest)
# Print rows 2000:2005
print(copData.iloc[2000:2005])
```

_output_

| Index | time  | copX  | copY  | leftCopX | leftCopY | rightCopX | rightCopY |
|-------|-------|-------|-------|----------|----------|-----------|-----------|
| 2000  | 2.001 | 1.20  | 0.40  | 1.00     | 0.20     | 1.40      | 0.60      |
| 2001  | 2.002 | 1.30  | 0.50  | 1.10     | 0.30     | 1.50      | 0.70      |
| 2002  | 2.003 | 1.40  | 0.60  | 1.20     | 0.40     | 1.60      | 0.80      |
| 2003  | 2.004 | 1.50  | 0.70  | NaN      | NaN      | 1.70      | 0.90      |
| 2004  | 2.005 | 1.60  | 0.80  | NaN      | NaN      | 1.80      | 1.00      |
