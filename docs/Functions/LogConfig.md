__`LogConfig(file: bool = "False, level: str = "info")`__

### Description
Configure logging for the application based on user preferences or defaults.

### Parameters
__`file`__: (_bool_) If True, logs will be written to a file. If False, logs will be written to stdout.

__`level`__: (_str_) Desired log level. Valid values are 'debug', 'info', 'warning', 'error', 'critical'.

### Raises
**Value Error**

* If invalid option for level.

### Example

``` Python title="Create Log File At Lowest Level"
from hdforce import LogConfig

LogConfig(file = True, level = "debug")
```