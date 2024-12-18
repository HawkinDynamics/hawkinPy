__`BuildDB(start_date: str, test_type: str = "all", include_inactive: bool = False, file_name: str,  file_type: str = "csv", span: int = 14)`__

### Description
This function builds a database of prior test data from a set amount of prior days until today. It allows setting increments to control the number of days downloaded at a time for more efficient download speeds. The default span is 14, meaning tests will download in 14-day increments.

### Parameters
__`start_date`__: _(str)_ A date string or numeric value representing the starting date for retrieving test data. Date string must be format "YYYY-MM-DD", or numerical value as EPOCH timestamp.

__`test_type`__: _(str)_ A character string representing the type of test to retrieve. Defaults to `"all"`. Can be a specific test type.

__`include_inactive`__: _(bool)_ A logical value indicating whether to include inactive tests. Defaults to `FALSE`.

__`file_name`__: _(str)_ A character string representing the name of the file to save the database.

__`file_type`__: _(str)_ A character string specifying the format of the file to save. Supported formats include 'csv', 'xlsx', 'parquet', 'feather'. Defaults to 'csv'.

__`span`__: _(int)_ An integer value indicating the number of days to download in each increment. Defaults to 14.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import BuildDB

# Build locally stored database of tests
BuildDB(
  start_date = "2024-01-01",
  test_type = "all",
  include_inactive = False,
  file_name = "C:/Users/My-Force-Plate-Project/my-database",
  file_type = "csv",
  span = 60
)

```

_output_
none