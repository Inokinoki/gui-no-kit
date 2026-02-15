# Xpra GUI Test Framework

A Python framework for automated GUI testing of applications using Xpra's HTML5 client and Playwright browser automation.

## Overview

`gui-no-kit` enables you to test GUI applications across multiple platforms by:

1. Running applications in an Xpra server with WebSocket/HTML5 access
2. Using Playwright to control a browser and interact with the rendered GUI
3. Automatically managing server lifecycle per test
4. Capturing server logs and screenshots for debugging failures

**Multi-Platform Support:**
- **Linux/X11**: Test X11 applications with optional Xvfb for headless CI/CD
- **macOS**: Test native macOS applications (Cocoa backend)
- **Windows**: Test Windows applications (GDI backend)

**Use case:** Automated GUI testing of desktop applications in CI/CD pipelines across platforms.

## Requirements

### System Requirements

- **Xpra server** - Install from [xpra.org](https://xpra.org/) or your distribution
  ```bash
  # Ubuntu/Debian
  sudo apt install xpra

  # Fedora/RHEL
  sudo dnf install xpra

  # macOS
  brew install xpra

  # Windows
  # Download from https://xpra.org/
  ```

- **Platform-specific requirements:**

  **Linux/X11:**
  - **Xvfb** (optional, for headless operation)
    ```bash
    sudo apt install xvfb  # Ubuntu/Debian
    sudo dnf install xorg-x11-server-Xvfb  # Fedora/RHEL
    ```
  - X11 applications to test (e.g., xeyes, xcalc, xterm)

  **macOS:**
  - Native macOS applications (no Xvfb needed)
  - Or XQuartz for X11 applications

  **Windows:**
  - Windows applications (no Xvfb needed)
  - Or Xpra's X11 support for X11 applications

### Python Dependencies

```bash
pip install pytest playwright
playwright install chromium
```

## Installation

```bash
# From the xpra repository
cd xpra
pip install -e .

# Or install dependencies manually
pip install pytest playwright psutil
playwright install chromium
```

## Quick Start

### Linux/X11 Example

```python
from gui_no_kit import XpraGUITestCase

class TestXeyes(XpraGUITestCase):
    def test_xeyes_opens(self):
        """Test that xeyes displays correctly."""
        gui = self.start_gui("xeyes", use_xvfb=True)  # Use Xvfb for headless
        gui.wait_for_canvas()

        # Take screenshot for visual verification
        gui.screenshot("/tmp/xeyes.png")

        # Verify canvas is rendering
        self.assert_canvas_visible()
```

### macOS Example

```python
from gui_no_kit import XpraGUITestCase

class TestTextEdit(XpraGUITestCase):
    def test_textedit_opens(self):
        """Test that TextEdit displays correctly."""
        # On macOS, no Xvfb needed - uses native Cocoa display
        gui = self.start_gui("/Applications/TextEdit.app/Contents/MacOS/TextEdit")
        gui.wait_for_canvas()
        gui.screenshot("/tmp/textedit.png")
```

### Windows Example

```python
from gui_no_kit import XpraGUITestCase

class TestNotepad(XpraGUITestCase):
    def test_notepad_opens(self):
        """Test that Notepad displays correctly."""
        # On Windows, no Xvfb needed - uses native GDI display
        gui = self.start_gui("notepad.exe")
        gui.wait_for_canvas()
        gui.screenshot("C:\\temp\\notepad.png")
```

### Using pytest fixtures

```python
def test_xcalc(xpra_server):
    """Test xcalc using pytest fixtures."""
    from gui_no_kit import PlaywrightClient

    # Start server (use_xvfb only applies on Linux)
    ws_url = xpra_server.start("xcalc", use_xvfb=True)

    # Connect client
    client = PlaywrightClient(ws_url, headless=True)
    client.connect()

    # Test
    client.wait_for_canvas()
    client.screenshot("/tmp/xcalc.png")

    # Cleanup
    client.disconnect()
```

## Platform Support

The framework supports testing GUI applications on multiple platforms:

### Linux/X11

- **Display System**: X11
- **Headless Operation**: Xvfb (virtual X11 display)
- **Applications**: X11 applications (xeyes, xcalc, xterm, etc.)
- **Example**:
  ```python
  gui = self.start_gui("xeyes", use_xvfb=True)  # Use Xvfb for headless CI/CD
  ```

### macOS

- **Display System**: Native Cocoa (no Xvfb needed)
- **Headless Operation**: Supported via CI runner virtual display
- **Applications**: Native macOS apps or X11 apps via XQuartz
- **Example**:
  ```python
  gui = self.start_gui("/Applications/TextEdit.app/Contents/MacOS/TextEdit")
  # Note: use_xvfb parameter is ignored on macOS (not needed)
  ```

### Windows

- **Display System**: Windows GDI (no Xvfb needed)
- **Headless Operation**: Supported via CI runner virtual display
- **Applications**: Windows applications
- **Example**:
  ```python
  gui = self.start_gui("notepad.exe")
  # Note: use_xvfb parameter is ignored on Windows (not needed)
  ```

### Cross-Platform Considerations

- **use_xvfb parameter**: Only applies to Linux/X11 systems
- **HTML5/WebSocket client**: Works identically on all platforms
- **Playwright browser**: Same automation API regardless of platform
- **Portability**: Tests written once work on all platforms (with app_command adjusted)

### CI/CD Recommendations

| Platform | Headless Support | How It Works | Example CI Services |
|----------|------------------|--------------|-------------------|
| Linux | ✅ Xvfb (virtual display) | Creates virtual X11 display without physical monitor | Any CI (Docker, bare metal, etc.) |
| macOS | ✅ Virtual display | CI runner provides virtual/framebuffer display | GitHub Actions, Buildbot, Cirrus CI |
| Windows | ✅ Virtual display | CI runner provides virtual/framebuffer display | GitHub Actions, Azure DevOps, Buildbot |

**Key Point**: All platforms support headless GUI testing! The difference is:
- **Linux**: Uses Xvfb to create a virtual display anywhere
- **macOS/Windows**: Rely on CI runner's built-in virtual display capabilities

## API Reference

### XpraServer

Manages Xpra server lifecycle.

```python
from gui_no_kit import XpraServer

server = XpraServer(host="127.0.0.1", port=None)  # Auto-assign port
ws_url = server.start("xeyes", use_xvfb=True)
# ws_url = "ws://127.0.0.1:14523/"

# Check if running
assert server.is_running()

# Get logs for debugging
logs = server.get_logs()

# Stop server
server.stop()
```

**Methods:**
- `start(app_command, extra_args=None, use_xvfb=True)` - Start server with app
- `stop(timeout=10)` - Stop server
- `get_logs()` - Get captured stdout/stderr
- `is_running()` - Check if server process is alive

### PlaywrightClient

Controls browser for HTML5 client interaction.

```python
from gui_no_kit import PlaywrightClient

client = PlaywrightClient(ws_url="ws://127.0.0.1:14523/", headless=True)
client.connect()

# Wait for canvas to be ready
client.wait_for_canvas(timeout=10000)

# Take screenshot
client.screenshot("/tmp/app.png")

# Get canvas dimensions
width, height = client.get_canvas_size()

# Execute JavaScript
result = client.execute_script("document.title")

# Disconnect
client.disconnect()
```

**Methods:**
- `connect()` - Launch browser and navigate to HTML5 client
- `disconnect()` - Close browser
- `screenshot(path)` - Save screenshot of canvas
- `wait_for_canvas(timeout=10000)` - Wait for Xpra canvas
- `get_canvas_size()` - Get canvas dimensions as (width, height)
- `click(selector, timeout=5000)` - Click element
- `click_canvas_at(x, y)` - Click canvas at coordinates
- `execute_script(script, *args)` - Execute JavaScript

### XpraGUITestCase

Base class for unittest tests with automatic lifecycle management.

```python
from gui_no_kit import XpraGUITestCase

class TestMyApp(XpraGUITestCase):
    def test_something(self):
        # Start GUI app
        gui = self.start_gui("xcalc")

        # Test
        self.assert_canvas_visible()

        # Screenshot on failure is automatic
```

**Methods:**
- `start_gui(app_command, headless=True, use_xvfb=True)` - Start app and return client
- `get_server_logs()` - Get captured logs
- `save_screenshot(path)` - Save screenshot
- `assert_canvas_visible(timeout=5000)` - Assert canvas is visible
- `assert_server_running()` - Assert server is running

**Automatic on failure:**
- Screenshot saved to `/tmp/xpra_test_fail_<test_name>.png`
- Server logs printed to stdout

## Running Tests

### Run all example tests

```bash
# Using pytest
pytest gui_no_kit/examples/example_tests.py

# Using unittest
python -m unittest gui_no_kit.examples.example_tests

# Run specific test
pytest gui_no_kit/examples/example_tests.py::TestXeyes::test_xeyes_opens
```

### Run with visual output (headful mode)

```python
gui = self.start_gui("xeyes", headless=False)
```

## Advanced Usage

### Custom xpra arguments

```python
gui = self.start_gui(
    "xterm",
    extra_args=["--start-child=ls", "--encoding=rgb"]
)
```

### Without Xvfb (use existing display)

```python
gui = self.start_gui("xeyes", use_xvfb=False)
```

### Context manager for client

```python
with PlaywrightClient(ws_url, headless=True) as client:
    client.wait_for_canvas()
    client.screenshot("/tmp/test.png")
# Auto-disconnect
```

### Pytest markers

```python
import pytest

@pytest.mark.gui
@pytest.mark.slow
def test_slow_gui(xpra_server):
    # ...
    pass

# Run only GUI tests
pytest -m gui

# Skip slow tests
pytest -m "not slow"
```

## Troubleshooting

### Server fails to start

```bash
# Check xpra installation
which xpra
xpra version

# Check Xvfb
which Xvfb

# Run with debug output
XPRA_TEST_DEBUG=1 pytest test_file.py
```

### Canvas not found

```bash
# Increase timeout
client.wait_for_canvas(timeout=30000)

# Run headless to see what's happening
gui = self.start_gui("xeyes", headless=False)
```

### Port already in use

```python
# Specify a different port
server = XpraServer(host="127.0.0.1", port=9999)
```

### Browser issues

```bash
# Reinstall playwright browsers
playwright install chromium --force
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Code (pytest/unittest)              │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌────────────────────┐        ┌────────────────────┐
│  XpraServer        │        │  PlaywrightClient  │
│  - start/stop      │◄───────│  - browser control │
│  - log capture     │        │  - element find    │
│  - display mgmt    │        │  - screenshot      │
└─────────┬──────────┘        └─────────┬──────────┘
          │                             │
          │ Xpra protocol               │ WebSocket
          │ (bind-ws)                   │ HTML5 client
          ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Xpra Server + HTTP/WebSocket             │
└─────────────────────────────────────────────────────────────┘
          │
          │ X11 protocol
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      GUI Application                        │
└─────────────────────────────────────────────────────────────┘
```

## CI/CD Examples

### GitHub Actions - Linux (with Xvfb)

```yaml
name: GUI Tests (Linux)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y xpra xvfb
          pip install pytest playwright
          playwright install chromium
      - name: Run GUI tests
        run: pytest gui_no_kit/examples/example_tests.py -v
```

### GitHub Actions - Multi-Platform

```yaml
name: GUI Tests (All Platforms)

on: [push, pull_request]

jobs:
  test-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          sudo apt-get install -y xpra xvfb
          pip install pytest playwright
          playwright install chromium
      - name: Run Linux GUI tests
        run: pytest gui_no_kit/examples/example_tests.py::TestXeyes -v

  test-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          brew install xpra
          pip install pytest playwright
          playwright install chromium
      - name: Run macOS GUI tests
        run: pytest gui_no_kit/examples/example_tests.py::TestCrossPlatform::test_macos_native_app -v

  test-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          # Install xpra for Windows (download from xpra.org)
          pip install pytest playwright
          playwright install chromium
      - name: Run Windows GUI tests
        run: pytest gui_no_kit/examples/example_tests.py::TestCrossPlatform::test_windows_app -v
```

### GitLab CI - Linux (with Docker)

```yaml
# .gitlab-ci.yml
stages:
  - test

gui-tests-linux:
  stage: test
  image: ubuntu:22.04
  script:
    - apt-get update && apt-get install -y
        xpra
        xvfb
        python3
        python3-pip
    - pip3 install pytest playwright
    - playwright install chromium --with-deps
    - pytest gui_no_kit/examples/example_tests.py -v
  artifacts:
    when: on_failure
    paths:
      - /tmp/xpra_test_fail_*.png
    expire_in: 1 week

gui-tests-linux-docker:
  stage: test
  image: python:3.11-slim
  services:
    - xvfb:xvfb
  before_script:
    - apt-get update && apt-get install -y xpra
    - pip install pytest playwright
    - playwright install chromium --with-deps
  script:
    - export DISPLAY=:99
    - Xvfb :99 -screen 0 1280x1024x24 &
    - sleep 2
    - pytest gui_no_kit/examples/example_tests.py -v
```

### GitLab CI - Multi-Platform

```yaml
# .gitlab-ci.yml
stages:
  - test

gui-tests-linux:
  stage: test
  image: ubuntu:22.04
  script:
    - apt-get update && apt-get install -y xpra xvfb python3-pip
    - pip3 install pytest playwright
    - playwright install chromium
    - pytest gui_no_kit/examples/example_tests.py::TestXeyes -v
  tags:
    - linux
  artifacts:
    paths:
      - /tmp/*.png
    when: on_failure

gui-tests-macos:
  stage: test
  script:
    - brew install xpra
    - pip3 install pytest playwright
    - playwright install chromium
    - pytest gui_no_kit/examples/example_tests.py::TestCrossPlatform::test_macos_native_app -v
  tags:
    - macos

gui-tests-windows:
  stage: test
  script:
    - # Install xpra for Windows (pre-installed or download)
    - pip install pytest playwright
    - playwright install chromium
    - pytest gui_no_kit/examples/example_tests.py::TestCrossPlatform::test_windows_app -v
  tags:
    - windows
```

### Jenkins - Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    sudo apt-get update
                    sudo apt-get install -y xpra xvfb
                    pip3 install pytest playwright
                    playwright install chromium
                '''
            }
        }

        stage('Run GUI Tests') {
            steps {
                sh '''
                    export DISPLAY=:99
                    Xvfb :99 -screen 0 1280x1024x24 &
                    sleep 2
                    pytest gui_no_kit/examples/example_tests.py -v \
                        --junitxml=test-results.xml \
                        --html=test-report.html
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: '*.png', allowEmptyArchive: true
                junit 'test-results.xml'
                publishHTML(target: [
                    reportDir: '.',
                    reportFiles: 'test-report.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }

    post {
        always {
            sh 'pkill -9 Xvfb || true'
        }
        failure {
            sh 'echo "Check screenshots in artifacts for failure analysis"'
        }
    }
}
```

### Jenkins - Declarative Pipeline with Docker

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '--privileged -e DISPLAY=:99'
        }
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    apt-get update && apt-get install -y xpra xvfb
                    pip install pytest playwright
                    playwright install chromium --with-deps
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    Xvfb :99 -screen 0 1280x1024x24 &
                    export DISPLAY=:99
                    sleep 2
                    pytest gui_no_kit/examples/example_tests.py -v
                '''
            }
        }
    }
}
```

### Azure DevOps - Linux Pipeline

```yaml
# azure-pipelines.yml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- script: |
    sudo apt-get update
    sudo apt-get install -y xpra xvfb
  displayName: 'Install Xpra and Xvfb'

- script: |
    pip install pytest playwright
    playwright install chromium
  displayName: 'Install Python dependencies'

- script: |
    export DISPLAY=:99
    Xvfb :99 -screen 0 1280x1024x24 &
    sleep 2
    pytest gui_no_kit/examples/example_tests.py -v \
        --junitxml=test-results.xml
  displayName: 'Run GUI tests'

- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'test-results.xml'
    testRunTitle: 'GUI Tests'

- publish: '/tmp/*.png'
  artifact: screenshots
  condition: failed()
```

### Azure DevOps - Multi-Platform Pipeline

```yaml
# azure-pipelines.yml
trigger:
- main

stages:
- stage: Linux
  jobs:
  - job: 'GUI_Tests'
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - script: |
        sudo apt-get install -y xpra xvfb
        pip install pytest playwright
        playwright install chromium
      displayName: 'Install dependencies'
    - script: |
        export DISPLAY=:99
        Xvfb :99 -screen 0 1280x1024x24 &
        pytest gui_no_kit/examples/example_tests.py::TestXeyes -v
      displayName: 'Run tests'

- stage: macOS
  jobs:
  - job: 'GUI_Tests'
    pool:
      vmImage: 'macOS-latest'
    steps:
    - script: |
        brew install xpra
        pip3 install pytest playwright
        playwright install chromium
      displayName: 'Install dependencies'
    - script: |
        pytest gui_no_kit/examples/example_tests.py::TestCrossPlatform::test_macos_native_app -v
      displayName: 'Run tests'

- stage: Windows
  jobs:
  - job: 'GUI_Tests'
    pool:
      vmImage: 'windows-latest'
    steps:
    - script: |
        pip install pytest playwright
        playwright install chromium
      displayName: 'Install dependencies'
    - script: |
        pytest gui_no_kit/examples/example_tests.py::TestCrossPlatform::test_windows_app -v
      displayName: 'Run tests'
```

### CircleCI - Linux

```yaml
# .config/config.yml
version: 2.1

orbs:
  browser-tools: circleci/browser-tools@1.2.3

jobs:
  gui-tests:
    docker:
      - image: cimg/python:3.11
    resource_class: large
    steps:
      - checkout
      - browser-tools/install-browser-tools
      - run:
          name: Install Xpra and Xvfb
          command: |
            sudo apt-get update
            sudo apt-get install -y xpra xvfb
      - run:
          name: Install Python dependencies
          command: |
            pip install pytest playwright
            playwright install chromium
      - run:
          name: Run GUI tests
          command: |
            export DISPLAY=:99
            Xvfb :99 -screen 0 1280x1024x24 &
            sleep 2
            pytest gui_no_kit/examples/example_tests.py -v
          environment:
            DISPLAY: :99
      - store_artifacts:
          path: /tmp/*.png
          destination: screenshots
          when: on_fail

workflows:
  gui-test-workflow:
    jobs:
      - gui-tests
```

### Buildbot - Build Master Configuration

```python
# buildbot.cfg
from buildbot.plugins import steps, util

# Factory for Linux GUI tests
linux_gui_factory = util.BuildFactory()
linux_gui_factory.addStep(steps.ShellCommand(
    name="Install dependencies",
    command=["sudo", "apt-get", "install", "-y", "xpra", "xvfb"]
))
linux_gui_factory.addStep(steps.ShellCommand(
    name="Install Python packages",
    command=["pip", "install", "pytest", "playwright"]
))
linux_gui_factory.addStep(steps.ShellCommand(
    name="Install Chromium",
    command=["playwright", "install", "chromium"]
))
linux_gui_factory.addStep(steps.ShellCommand(
    name="Start Xvfb",
    command=["Xvfb", ":99", "-screen", "0", "1280x1024x24"],
    env={"DISPLAY": ":99"}
))
linux_gui_factory.addStep(steps.ShellCommand(
    name="Run GUI tests",
    command=["pytest", "gui_no_kit/examples/example_tests.py", "-v"],
    env={"DISPLAY": ":99"}
))

# Builder
c['builders'].append(util.BuilderConfig(
    name="linux-gui-tests",
    workernames=["linux-worker"],
    factory=linux_gui_factory
))

# Scheduler
c['schedulers'].append(util.ForceScheduler(
    name="force-gui-tests",
    builderNames=["linux-gui-tests"]
))
```

### Docker Compose - Local Testing

```yaml
# docker-compose.yml
version: '3.8'

services:
  gui-tests:
    build: .
    volumes:
      - ./gui_no_kit:/app/gui_no_kit
      - ./test-results:/tmp/test-results
    environment:
      - DISPLAY=:99
    cap_add:
      - SYS_ADMIN
    command: >
      bash -c "
        Xvfb :99 -screen 0 1280x1024x24 &&
        sleep 2 &&
        pytest gui_no_kit/examples/example_tests.py -v
      "

# Dockerfile
# FROM python:3.11-slim
# RUN apt-get update && apt-get install -y xpra xvfb
# RUN pip install pytest playwright
# RUN playwright install chromium --with-deps
# WORKDIR /app
# COPY . .
```

### tox - Multi-Environment Testing

```ini
# tox.ini
[tox]
envlist = py{310,311,312}-gui
skipsdist = True

[testenv]
deps =
    pytest
    playwright
commands =
    playwright install chromium
    pytest gui_no_kit/examples/example_tests.py {posargs:-v}

[testenv:py{310,311,312}-gui]
platform =
    linux: linux
    macos: darwin
    windows: win32
setenv =
    linux: DISPLAY=:99
commands_pre =
    linux: Xvfb :99 -screen 0 1280x1024x24 || true
    linux: sleep 2
```

### Argo Workflows - Kubernetes

```yaml
# gui-tests-workflow.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: gui-tests-
spec:
  entrypoint: gui-tests
  templates:
  - name: gui-tests
    steps:
    - - name: install-deps
        template: install-deps
      - name: run-tests
        template: run-tests

  - name: install-deps
    container:
      image: ubuntu:22.04
      command: [sh, -c]
      args:
        - |
          apt-get update
          apt-get install -y xpra xvfb python3-pip
          pip3 install pytest playwright
          playwright install chromium
      volumeMounts:
      - name: test-data
        mountPath: /data

  - name: run-tests
    container:
      image: ubuntu:22.04
      command: [sh, -c]
      args:
        - |
          export DISPLAY=:99
          Xvfb :99 -screen 0 1280x1024x24 &
          sleep 2
          pytest gui_no_kit/examples/example_tests.py -v
      env:
      - name: DISPLAY
        value: ":99"
      volumeMounts:
      - name: test-data
        mountPath: /data
    volumes:
    - name: test-data
      emptyDir: {}
```

## Contributing

This framework is part of the Xpra project. Contributions are welcome!

- Source: https://github.com/Xpra-org/xpra
- Issues: https://github.com/Xpra-org/xpra/issues

## License

GPL v2 or later (same as Xpra)

See COPYING file for details.
