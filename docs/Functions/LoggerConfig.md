__`LoggerConfig.Configuration(file: bool = "False, level: str = "info", file_path: str=None, file_mode: str = 'a')`__

### Description
Configure logging for the application based on user preferences or defaults.

### Parameters
__`file`__: (_bool_) If True, logs will be written to a file. If False, logs will be written to stdout.

__`level`__: (_str_) Desired log level. Valid values are 'debug', 'info', 'warning', 'error', 'critical'.

__`file_path`__: (str) The full path where the log file will be saved. Defaults to 'hdforce.log' in the current project directory.

__`file_mode`__: (str) Mode to open the log file, default is 'a'. Options are 'a' (append) and 'w'(overwrite)

### Raises
**Value Error**

* If invalid option for level.

### Example

``` Python title="Create Log File At Lowest Level"
from hdforce import LoggerConfig

LoggerConfig.Configuration(file = True, level = "debug")
```