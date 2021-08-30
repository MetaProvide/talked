# Changelog

## [Unreleased]

### Added

-   [#25](https://github.com/MetaProvide/talked/issues/25) Executable that gets installed on install
-   [#28](https://github.com/MetaProvide/talked/issues/28) Commandline arguments to control host and port the internal server will bind to.

### Changed

-   [#27](https://github.com/MetaProvide/talked/issues/27) Remove uWSGI as a runtime dependency in pyproject file

## 0.1.5 - 2021-08-25

### Fixed

-   [#19](https://github.com/MetaProvide/talked/issues/19) Make the .stripe-wrapper rule important to make sure it applies, and hide grid navigation arrow.

## 0.1.4 - 2021-08-23

### Added

-   Proper CHANGELOG

### Fixed

-   Switch to using yuv420 instead of yuv444 for recording so it can be played in Firefox.
-   Change ProtectHome from strict to full in the example systemd unit file.
