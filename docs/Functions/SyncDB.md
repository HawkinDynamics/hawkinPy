__`SyncDB(file: str, include_inactive: bool = False, new_file: str)`__

### Description
This function reads an existing database from the specified file and updates it by fetching new tests and updating any changes to existing tests. It supports multiple file types and saves the updated database back to the original file. Supported file formats include CSV, XLSX, Feather, and Parquet.

### Parameters
__`file`__: _(str)_ The path to the current database file. Supported file types include 'csv', 'xlsx', 'feather', and 'parquet'.

__`include_inactive`__: _(bool)_ A logical value indicating whether to include inactive tests. Defaults to `FALSE`.

__`new_file`__: _(str)_ Provide a new file path to save the updated database. If None, overwrites the original file.

### Raises
**Exception**

* No Access Token Found.
* If the HTTP response status is not 200, indicating an unsuccessful API request, or if there is a failure in parsing the JSON response.


### Example

``` Python
from hdforce import SyncDB

# Build locally stored database of tests
SyncDB(
  file_name = "C:/Users/My-Force-Plate-Project/my-database",
  include_inactive = False,
  new_file = "C:/Users/My-Force-Plate-Project/my-new-database"
)

```

_output_
none
