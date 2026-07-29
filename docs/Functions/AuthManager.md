__`AuthManager(region: str = "Americas", authMethod: str = "env", refreshToken_name: str = "HD_REFRESH_TOKEN", refreshToken: str = None, env_file_name: str = None)`__

### Description
Choose the authentication method and settings for your project environment. If you want to store or replace your refresh token, simply pass it in the  `refreshToken` argument (unless `authMethod` set to "manual").

### Parameters
__`region`__: (_str_) The region that designates the url prefix. Defaults to "Americas". Other options include "Americas", "Europe", and "Asia/Pacific".

__`authMethod`__: (_str_) Determine method of storing authentication variables, including refresh token. One of 'env', 'file', 'manual', 'keyring'. To store variables in your local system environment, use "env". To store variables in a .env file, use "file". To authenticate without storing your refresh token and region, use "manual". To store the refresh token securely in your operating system's credential store (macOS Keychain, Windows Credential Manager, Linux Secret Service), use "keyring" — pass `refreshToken` the first time to store it, then omit it in later sessions to read it back. Requires the [keyring](https://pypi.org/project/keyring/) package (installed with hdforce).

__`refreshToken_name`__: (_str_) Name of refresh token variable saved in system environment or .env file. Template .env file shows this as "HD_REFRESH_TOKEN".

__`refreshToken`__: (_str_) If used with `authMethod = "manual"`, token will be used to authenticate without being stored. Else, token will be store/set as the new refresh token value with method selected.

__`env_file_name`__: (_str_) Required with `authMethod = "file"`. Provide the file path (relative to the root of the project) and name for variable storage. Just like the example below, the template file can be simply be saved as ".env". But the file can be given any name, followed by ".env".

### Raises
**Value Error**

* If authMethod not one of env, file, manual, or keyring.
* If authMethod = 'file' and no file name provided
* If authMethod = 'manual' and no refreshToken provided

### Example

``` Python title="Default Authentication Using Environment Variables"
from hdforce import AuthManager

AuthManager()
```

``` Python title="OS Keychain (keyring)"
from hdforce import AuthManager

# First time: pass refreshToken to store it in the OS keychain
AuthManager(authMethod="keyring", region="Americas", refreshToken="your_refresh_token")

# Later sessions: omit refreshToken to read it back from the keychain
AuthManager(authMethod="keyring", region="Americas")

# Multiple orgs: store separate profiles under distinct names
AuthManager(authMethod="keyring", refreshToken_name="HD_TEAM_B", refreshToken="team_b_token", region="Europe")
AuthManager(authMethod="keyring", refreshToken_name="HD_TEAM_B", region="Europe")
```