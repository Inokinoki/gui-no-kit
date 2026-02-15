"""
Base test class for Xpra GUI testing.

Combines XpraServer and PlaywrightClient into a convenient test base class
with automatic lifecycle management and failure debugging support.
"""

import os
import unittest
from typing import Optional

from .server import XpraServer
from .client import PlaywrightClient


class XpraGUITestCase(unittest.TestCase):
    """
    Base class for writing Xpra GUI tests.

    Provides automatic server lifecycle management, client connections,
    and failure debugging with screenshots and server logs.

    Example:
        class TestXeyes(XpraGUITestCase):
            def test_opens(self):
                gui = self.start_gui("xeyes")
                gui.wait_for_canvas()
                gui.screenshot("/tmp/xeyes.png")
    """

    def setUp(self) -> None:
        """Set up test environment before each test."""
        self.server: Optional[XpraServer] = None
        self.client: Optional[PlaywrightClient] = None

    def tearDown(self) -> None:
        """Clean up after each test."""
        # Disconnect client if still connected
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.client = None

        # Stop server if still running
        if self.server:
            try:
                self.server.stop()
            except Exception:
                pass
            self.server = None

    def start_gui(
        self,
        app_command: str,
        headless: bool = True,
        use_xvfb: bool = True,
        extra_args=None,
    ) -> PlaywrightClient:
        """
        Start a GUI application and return connected client.

        Args:
            app_command: Command to start (e.g., "xeyes", "xcalc")
            headless: Whether to run browser in headless mode
            use_xvfb: Whether to use Xvfb for virtual display
            extra_args: Additional arguments for xpra

        Returns:
            Connected PlaywrightClient instance

        Raises:
            RuntimeError: If server or client fails to start
        """
        if self.server:
            raise RuntimeError("Server already running")

        # Start server
        self.server = XpraServer()
        ws_url = self.server.start(
            app_command,
            extra_args=extra_args,
            use_xvfb=use_xvfb,
        )

        # Connect client
        self.client = PlaywrightClient(ws_url, headless=headless)
        self.client.connect()

        return self.client

    def get_server_logs(self) -> str:
        """
        Get captured server logs for debugging.

        Returns:
            All captured stdout and stderr from server
        """
        if not self.server:
            return "No server running"
        return self.server.get_logs()

    def save_screenshot(self, path: str) -> None:
        """
        Save a screenshot of the current GUI state.

        Args:
            path: File path to save screenshot

        Raises:
            RuntimeError: If no client is connected
        """
        if not self.client:
            raise RuntimeError("No client connected")
        self.client.screenshot(path)

    def run(self, result=None) -> None:
        """
        Override run to add failure hook.

        Captures screenshot and server logs on test failure.
        """
        # Run the test
        super().run(result)

        # Check if test failed
        try:
            if result and hasattr(result, 'failures') and result.failures:
                # Get the last failure
                test, traceback = result.failures[-1]
                if test == self:
                    self._run_failed_hook(result.failures[-1])
        except AttributeError:
            # pytest compatibility - result object is different
            pass

    def _run_failed_hook(self, failure_info) -> None:
        """
        Called on test failure to capture debugging information.

        Saves screenshot and prints server logs.

        Args:
            failure_info: Tuple of (test_case, traceback)
        """
        print("\n" + "=" * 70)
        print("TEST FAILED - Capturing debugging information")
        print("=" * 70)

        # Save screenshot
        if self.client:
            screenshot_path = f"/tmp/xpra_test_fail_{self.id()}.png"
            try:
                self.client.screenshot(screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
            except Exception as e:
                print(f"Failed to save screenshot: {e}")

        # Print server logs
        print("\n--- Server Logs ---")
        logs = self.get_server_logs()
        if logs:
            print(logs)
        else:
            print("(no logs captured)")

        print("=" * 70 + "\n")

    def assert_canvas_visible(self, timeout: int = 5000) -> None:
        """
        Assert that the Xpra canvas is visible.

        Args:
            timeout: Maximum time to wait in milliseconds

        Raises:
            AssertionError: If canvas is not visible
            RuntimeError: If no client is connected
        """
        if not self.client:
            raise RuntimeError("No client connected")

        try:
            self.client.wait_for_canvas(timeout=timeout)
            canvas = self.client.page.locator("canvas").first
            assert canvas.is_visible(), "Canvas is not visible"
        except Exception as e:
            raise AssertionError(f"Canvas not visible: {e}")

    def assert_server_running(self) -> None:
        """
        Assert that the Xpra server is still running.

        Raises:
            AssertionError: If server is not running
        """
        if not self.server:
            raise AssertionError("No server instance")
        if not self.server.is_running():
            raise AssertionError("Server is not running")
