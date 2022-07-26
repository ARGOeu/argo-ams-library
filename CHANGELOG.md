# Changelog

## [0.5.8] - 2022-07-26

### Fixed

AM-264 argo-ams-library: Delete topic and sub doesn't use the x-api-key token

## [0.5.7] - 2022-06-22

### Fixed

AM-249 ams-library: bug fix regarding sub and topic acl methods #137

## [0.5.6] - 2022-06-21

### Added 

AM-233 ams-library: support for project_member_get api call
AM-230 ams-library: support for project_member_add api call
AM-229 ams-library: support for user_get api call
AM-226 ams-library: support for user_create api call

## [0.5.5] - 2021-04-15

### Added 

ARGO-2768 ams-library: support for AMS authorization header

## [0.5.4] - 2020-10-08

### Fixed

ARGO-2592 ams-library py2 RPM also packages py3 specific modules

## [0.5.3] - 2020-09-08

### Fixed

* ARGO-2530 bytes handling in Py3

## [0.5.2] - 2020-07-08

### Fixed 

* ARGO-2479 Modify subscription offset method fails
* ARGO-2360 Fix ack_sub retry loop

## [0.5.1] - 2020-02-12

### Fixed

* ARGO-2182 ams-lib does not retry on topic publish
* fixed RPM autodependencies so py2 RPM is no longer requiring py3 ABI
* replaced include in MANIFEST.in with graft

## [0.5.0] - 2019-12-19

### Added 

* ARGO-1481 Connection retry logic in ams-library

## [0.4.3] - 2019-11-08

### Added 

* ARGO-1862 Make argo-ams-library Python 3 ready
* ARGO-1841 Update the ams library to include the new timeToOffset functionality

## [0.4.2-1] - 2018-06-26

### Added

* ARGO-1120 Extend AMS client to support X509 method via the authentication

### Fixed

* Updated error handling
* Error handling bug during list_topic route and upgrade to v0.4.2

## [0.4.0-1] - 2018-05-09

### Added 

* Extend ams library to support offset manipulation
* Introduce AmsHttpRequests class
* Common methods for PUT, GET, POST requests
* Tests for backend error messages that could be plaintext or JSON encoded
* Failed TopicPublish and CreateSubscription tests
* Separated error mocks
* Extend ams library to support offset manipulation
* Grab methods from class namespace
* Tests for bogus offset specified
* Added missed 'all' value for offset argument
* Handle 404 for topic and subscription calls
* Handle JSON error message propagated through AMS

### Fixed 

* set for error codes and pass request args for iters
* Status msg attach to AmsServiceException if exist
* Topic ALREADY_EXIST error test
* Fix returnImmediately parameter in sub pull request
* Remove not raised TypeError exception handles
* Refactored error handling with error routes
* Offsets method with combined logic of get and move offsets

## [0.3.0-1] - 2017-07-27

### Added

* Sphinx documentation to ams library
* Add dockerfile that builds documentation

## [0.2.0-1] - 2017-06-08

### Added

* A simple library for interacting with the ARGO Messaging Service
