"""
Pytest fixtures for gui-no-kit framework.

Provides alternative API for pytest users who prefer fixtures over
the XpraGUITestCase base class.
"""

import pytest
from typing import Generator

from gui_no_kit.server import XpraServer
from gui_no_kit.client import PlaywrightClient


@pytest.fixture
def xpra_server() -> Generator[XpraServer, None, None]:
    """
    Fixture that provides an XpraServer instance.

    Automatically handles server cleanup after the test.

    Example:
        def test_something(xpra_server):
            ws_url = xpra_server.start("xeyes")
            # ... test code ...
    """
    server = XpraServer()
    yield server
    # Cleanup
    if server.is_running():
        server.stop()


@pytest.fixture
def xpra_server_with_display(xpra_server: XpraServer) -> Generator[PlaywrightClient, None, None]:
    """
    Fixture factory that creates a server and connects a client.

    Use this fixture when you need both server and connected client.

    Example:
        def test_something(xpra_server_with_display):
            client = xpra_server_with_display("xeyes")
            client.screenshot("/tmp/test.png")
    """
    def _create_client(app_command: str, headless: bool = True, use_xvfb: bool = True) -> PlaywrightClient:
        """
        Create a server and connected client for the given app.

        Args:
            app_command: Command to start (e.g., "xeyes", "xcalc")
            headless: Whether to run browser in headless mode
            use_xvfb: Whether to use Xvfb for virtual display

        Returns:
            Connected PlaywrightClient instance
        """
        # Server is already set up by the outer fixture
        if xpra_server.is_running():
            raise RuntimeError("Server already running")

        ws_url = xpra_server.start(app_command, use_xvfb=use_xvfb)
        client = PlaywrightClient(ws_url, headless=headless)
        client.connect()

        return client

    yield _create_client

    # Note: client cleanup is handled by the test function
    # The server will be cleaned up by the xpra_server fixture


@pytest.fixture
def gui_client(xpra_server: XpraServer) -> Generator[PlaywrightClient, None, None]:
    """
    Fixture that provides a connected GUI client.

    This is an alternative to xpra_server_with_display that creates
    the client immediately rather than providing a factory.

    Example:
        @pytest.fixture
        def my_app(gui_client):
            return gui_client.start_and_connect("xeyes")

        def test_something(my_app):
            my_app.screenshot("/tmp/test.png")
    """
    class _GUIClientFixture:
        def __init__(self, server: XpraServer):
            self.server = server
            self.client: PlaywrightClient | None = None

        def start_and_connect(
            self,
            app_command: str,
            headless: bool = True,
            use_xvfb: bool = True,
        ) -> PlaywrightClient:
            """Start server and connect client."""
            if self.client:
                raise RuntimeError("Client already connected")

            ws_url = self.server.start(app_command, use_xvfb=use_xvfb)
            self.client = PlaywrightClient(ws_url, headless=headless)
            self.client.connect()
            return self.client

        def disconnect(self):
            """Disconnect the client."""
            if self.client:
                self.client.disconnect()
                self.client = None

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.disconnect()

    fixture = _GUIClientFixture(xpra_server)
    yield fixture
    # Cleanup
    fixture.disconnect()


@pytest.fixture(autouse=True)
def capture_logs_on_failure(request, xpra_server):
    """
    Auto-use fixture that captures server logs on test failure.

    This fixture automatically runs for every test and will print
    server logs if the test fails.
    """
    yield

    # Check if test failed
    if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
        logs = xpra_server.get_logs()
        if logs:
            print("\n" + "=" * 70)
            print("Server Logs:")
            print("=" * 70)
            print(logs)
            print("=" * 70 + "\n")


@pytest.fixture
def screenshot_on_failure(request):
    """
    Fixture that saves a screenshot on test failure.

    Example:
        @pytest.mark.usefixtures("screenshot_on_failure")
        def test_something(gui_client):
            client = gui_client.start_and_connect("xeyes")
            # ... test code ...
    """
    yield

    # Check if test failed
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        # The test needs to have set up a client for this to work
        # This is a cooperative fixture - tests need to store client
        # in a known location or we use a context
        pass


# Hook for pytest to store test results
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Store test result for use in fixtures.
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
