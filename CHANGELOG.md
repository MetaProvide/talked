# Changelog

## [Unreleased]

## 0.3.2 - 2022-03-23

### Fixed

-   Make Nextcloud version comparison with int instead of string.

## 0.3.1 - 2022-01-11

### Fixed

-   nextcloud_version shouldn't be a list

## 0.3.0 - 2022-01-05

### Added

-   Support for Nextcloud 23
-   Finalise recording script option to run script after a recording has finished

### Fixed

-   [#39](https://github.com/MetaProvide/talked/issues/39) Hide "You seem to be talking while muted" tooltip with CSS
-   Click the mute button instead of using the keyboard shortcut as it seems to be more reliable
-   Switch to looking for a join call button that isn't disabled, makes startup time faster when everything is running smooth
-   Allow grid_view option to be overriden by talked client

## 0.2.1 - 2021-10-25

### Fixed

-   Fix close_sidebar function causing a TimeoutException as the HTML in Talk was changed

## 0.2.0 - 2021-09-30

### Added

-   [#25](https://github.com/MetaProvide/talked/issues/25) Executable that gets installed on install
-   [#28](https://github.com/MetaProvide/talked/issues/28) Commandline arguments to control host and port the internal server will bind to.
-   Add Makefile for handling dev environment
-   Add type hints
-   [#6](https://github.com/MetaProvide/talked/issues/6) Add option to record in grid view
-   [#23](https://github.com/MetaProvide/talked/issues/23) Add support for audio only recordings
-   [#20](https://github.com/MetaProvide/talked/issues/20) Verify support for python 3.7

### Changed

-   [#24](https://github.com/MetaProvide/talked/issues/24) Switch to toml for config file format
-   [#27](https://github.com/MetaProvide/talked/issues/27) Remove uWSGI as a runtime dependency in pyproject file
-   Recommend use of unix socket when running uwsgi behind webserver.

### Deprecated

-   JSON config files. Please use a toml config file instead. Support for json config files will be removed in version 0.3

### Fixed

-   [#21](https://github.com/MetaProvide/talked/issues/21) Remove hardcoded width and height parameters for launching Firefox

## 0.1.5 - 2021-08-25

### Fixed

-   [#19](https://github.com/MetaProvide/talked/issues/19) Make the .stripe-wrapper rule important to make sure it applies, and hide grid navigation arrow.

## 0.1.4 - 2021-08-23

### Added

-   Proper CHANGELOG

### Fixed

-   Switch to using yuv420 instead of yuv444 for recording so it can be played in Firefox.
-   Change ProtectHome from strict to full in the example systemd unit file.

