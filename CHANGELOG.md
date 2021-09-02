# Changelog

## [Unreleased]

### Added

-   [#25](https://github.com/MetaProvide/talked/issues/25) Executable that gets installed on install
-   [#28](https://github.com/MetaProvide/talked/issues/28) Commandline arguments to control host and port the internal server will bind to.
-   Add Makefile for handling dev environment

### Changed

-   [#24](https://github.com/MetaProvide/talked/issues/24) Switch to toml for config file format
-   [#27](https://github.com/MetaProvide/talked/issues/27) Remove uWSGI as a runtime dependency in pyproject file

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

