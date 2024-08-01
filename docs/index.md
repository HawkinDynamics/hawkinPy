# Getting Started With HDFORCE <img src="img/hdlogo_sm.png" align="left" alt="" width="120" />
**Get your data from the Hawkin Dynamics API**

<!-- badges: start -->
![GitHub Release](https://img.shields.io/github/v/release/HawkinDynamics/hawkinPy)
[![Test Py Versions and OS](https://github.com/HawkinDynamics/hawkinPy/actions/workflows/push-test.yml/badge.svg?branch=main)](https://github.com/HawkinDynamics/hawkinPy/actions/workflows/push-test.yml)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/HawkinDynamics/hawkinPy/main)
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![lifecycle](https://img.shields.io/badge/lifecycle-stable-green.svg)](https://www.tidyverse.org/lifecycle/#stable)
[![license](https://img.shields.io/badge/license-MIT%20+%20file%20LICENSE-lightgrey.svg)](https://choosealicense.com/)
<!-- badges: end -->

## The Force Is With You

HDFORCE provides simple functionality with Hawkin Dynamics API. These functions are for use with ‘Hawkin Dynamics Beta API’ version 1.10-beta. You must be an Hawkin Dynamics user with an active integration account to utilize functions within the package.

This API is designed to get data out of your Hawkin Dynamics server and interact with your data in a more intimate way. the motivation behind creating the package was to allow our HD users who develop and analyze in Python, to do so with less friction and more efficiency. Now you can access all of you data within just a couple lines of code. 

## How To Use The HDFORCE Package
The package was developed to be fairly straight-forward and easy to use. There are 3 steps involved:

1. Configure event logging (optional)
2. Authenticate your session
3. Get your data

__Logging Configuration__
For debugging and testing purposes, you have the option of creating a log file. The package has checkpoints within each function, that not only give descriptions of errors, but also give success checkpoints and details of call responses. By using the `LoggerConfig.Configure` function, you can set the minimum level of log type and whether to save the logs to a file. By default, logs are streamed to the console at the minimum level of 'info'.

__Authentication__
Using the `AuthManager`, you can configure some authentication settings specific to your development environment and gain access to your server. Once your session begins, you can simply use any of the other functions to get any and all of the data you ned from your organization. 

__Getting Your Data__

> As of July 10, 2024, `GetTestsAth`, `GetTestsType`, `GetTestsTeam`, and `GetTestsGroup` 
> have been deprecated for the preferred use of `GetTests`. This function will be fully 
> superseded Jan 01, 2025 12:00:00.

The API is not designed to be accessed from client applications directly. There is a limit on the amount of data that can be returned in a single request (256mb). As your database grows, it will be necessary to use the `from_` and `to_` parameters to limit the size of the responses. Responses that exceed the memory limit will timeout and fail. It is advised that you design your client to handle this from the beginning. A recommended pattern would be to have two methods of fetching data. A scheduled pull that uses the `from_` and `to_` parameters to constrain the returned data to only tests that have occurred since the last fetch e.g. every day or every 5 minutes. And then a pull that fetches the entire database since you began testing that is only executed when necessary. A recommended way of doing this is to generate the `from_` and `to_` parameters for each month since you started and send a request for each either in parallel or sequentially.
