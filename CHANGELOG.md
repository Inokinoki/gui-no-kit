# Changelog

All notable changes to gui-no-kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of gui-no-kit framework
- XpraServer class for managing Xpra server lifecycle
- PlaywrightClient class for browser automation
- XpraGUITestCase base class for unittest integration
- LogCapture class for non-blocking log capture
- pytest fixtures for pytest-style testing
- Multi-platform support (Linux/X11, macOS, Windows)
- Comprehensive documentation with CI/CD examples
- Support for headless testing with Xvfb (Linux)
- Example tests for xeyes, xcalc, xterm
- Cross-platform platform detection and error handling
- GitHub Actions, GitLab CI, Jenkins, Azure DevOps, CircleCI examples
- Docker Compose, Buildbot, tox, Argo Workflows examples

### Dependencies
- pytest >= 7.0
- playwright >= 1.40
- psutil >= 5.9

### Platform Support
- Linux/X11 with Xvfb for headless CI/CD
- macOS with native Cocoa display
- Windows with native GDI display

## [0.1.0] - TBD

### Planned Features
- Visual regression testing (screenshot comparison)
- Video recording of test executions
- Performance metrics collection
- Advanced element selectors (XPath, CSS)
- Wait conditions API
- Multi-window application support
- Clipboard testing utilities
- Keyboard/mouse event recording and replay
