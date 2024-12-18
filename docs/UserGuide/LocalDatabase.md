---
title: "Create and Sync Local Database"
output: html_document
---

## Overview

The `hdforce` Python package allows users to interact with the Hawkin Dynamics API to manage and analyze force platform and strain gauge data. This guide provides instructions for using the `BuildDB` and `SyncDB` functions to create and maintain a local database.

## Why Store Data Locally

To make a long story short, it's just easier for everyone. Data stored locally, or to a file, can be called and manipulated faster than retrieving the data from the cloud. Also, there are limitations to how much data can be called at once. Some of you may have come across this in the form of a 500 error when trying to call too many tests at once. And in reality, it is hard to say what the maximum number of tests is when querying via the API, as the size of the file returned will depend on a few factors. If you do analysis or create reports that utilize your entire database regularly, it might be a good idea to save your data to a local file. Here are a few benefits:

-   Faster calling and manipulation compared to API queries
-   Relatively small file sizes (compared to most modern storage capacities)
-   Easily update and maintain to stay in sync with remote server
-   Easily share or extend your analysis to other programs and machines

---

## Prerequisites

Before proceeding, ensure the following:

1. You have installed the `hdforce` package.
2. Your API credentials are properly configured (see the [Authentication](#authentication) section).
3. The necessary dependencies are installed:

```bash
pip install pandas requests python-dotenv
```

---

## Authentication

The `hdforce` package requires a valid API access token. Authentication is managed through the `AuthManager` class.

### Example:

```python
from hdforce.AuthManager import AuthManager

# Set up authentication
AuthManager(authMethod="file", env_file_name=".env")
```

For more details, see the [AuthManager documentation](#).

---

## How To Create Your Local Database Using `BuildDB`

Creating and maintaining a local database is as simple as a couple lines of code. After using the `AuthManager` for authentication, then execute the `BuildDB` function with the necessary parameters:

### Parameters

- `start_date` (str or int): The starting date for data retrieval, as a 'YYYY-MM-DD' string or Unix timestamp.
- `test_type` (str): The type of test data to retrieve (default is "all").
- `include_inactive` (bool): Whether to include inactive tests in the download (default is False).
- `file_name` (str): The name of the file to save the results.
- `file_type` (str): The format to save the file ('csv', 'xlsx', 'parquet', 'feather').
- `span` (int): The number of days to download at a time (default is 14).

### Example:

```python
from hdforce import BuildDB

# Build local database
BuildDB(start_date="2023-01-01",  file_name="my_database", file_type= "csv", span= 7)
```

---

# Updating Your Local Database With `SyncDB`

Now that you have a local database created. It is very simple to keep it up to date with new tests, or even edited past tests. The `SyncDB` function does most of the work. You just need to supply the path to the current database file. Then, like before, simply specify if you want the sync to include inactive tests. The function will identify the file type from the file extension, and if the database is of all test types or a particular unique test type, so no specification is needed.

If the file is saved in the same directory as the base of the working directory, you can simply provide the file name. Else, you need to provide the specific path.

You also have the option to create a new updated file with `SyncDB` by giving a new file path and name to the `new_file` parameter. While this is not necessary, this allows for safe updates with out overwrites. As the original file is still used to duplicate previous tests, and only new or synced tests are called. With the original file preserved, the user can choose which file to maintain or remove after review.

### Parameters

- `file` (str): The path to the current database file. Supported file types include 'csv', 'xlsx', 'feather', and 'parquet'.
- `include_inactive` (str): Whether to include inactive tests during sync (default is False).
- `new_file` (bool): Provide a new file path to save the updated database. If None, overwrites the original file.

### Example:

```python
from hdforce import SyncDB

# Sync local database
SyncDB(file_name="my_database.parquet")
```

And that's it! Your file will be saved back to it's original path (or in its new path).

Now you can manage your database locally and increase efficiency.

---

## FAQ

### Q: How do I handle authentication errors?
A: Ensure your API credentials are correct and that your `.env` file (if used) is properly configured. Use `AuthManager` to refresh tokens if needed.

### Q: Can I use a database format other than csv?
A: Currently, the `BuildDB` and `SyncDB` functions support csv, xlsx, feather, and parquet files.

---

For more information, visit the [hdforce documentation](#).
