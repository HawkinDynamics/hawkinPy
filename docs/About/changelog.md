# Changelogs

## hdforce v1.2.0

* Addition of `BuildDB` and `SyncDB` functions for storing and updating local database

* Addition of `last_sync_time` value to `GetTests` functions

* Changes to `GetTests` metric headers. Improved consistency of naming reflective of the metric library

* Improved functionality to `GetTests` to accept character strings in the format "YYYY-MM-DD" for `from` and `to`

* Addition of 'Metric Library' returned from `GetMetrics` 

* Improved functionality to `GetForceTime`to return all test types

## hdforce v1.1.2

* Bug fix: addition of new TruStrength test names and IDs to testTypeId validation method

## hdforce v1.1.1

* Corrected versioning and documentation

## hdforce v1.1.0

* Additions of CreateAthlete and UpdateAthlete functions
* Expansion of GetTests function to include 'team', 'group', type', and 'athlete' arguments
* Deprecation of GetTestsAth, GetTestsType, GetTestsTeam, and GetTestsGroup

## hdforce v1.0.01

* Initial release of production package
* Full logging configuration and Authentication features
* Tested on Python version 3.9 <-> 3.12, on Mac, Windows, and Linux

## hdforce v1.0.0rc0

* Improved logging
* bug fixes to GetTests functions
* Improved AuthMethods

## hdforce v0.0.0.1-beta

* Initial build for testing