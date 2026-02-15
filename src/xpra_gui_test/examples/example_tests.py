"""
Example tests demonstrating the gui-no-kit framework.

Shows different testing patterns using both the XpraGUITestCase base class
and pytest fixtures.

Platform Support:
- Linux/X11: X11 applications with optional Xvfb for headless operation
- macOS: Native macOS applications (Cocoa backend)
- Windows: Windows applications (GDI backend)
"""

import os
import platform
import tempfile
import unittest

from gui_no_kit import XpraGUITestCase


class TestBasicApp(XpraGUITestCase):
    """Example tests for basic applications on each platform."""

    def get_test_app(self):
        """Get platform-specific test application."""
        system = platform.system()
        if system == "Linux":
            return "xeyes"
        elif system == "Windows":
            return "notepad.exe"
        elif system == "Darwin":  # macOS
            return "TextEdit"
        else:
            raise NotImplementedError(f"No test app defined for {system}")

    def test_app_opens(self):
        """Test that the basic app displays correctly."""
        app = self.get_test_app()
        gui = self.start_gui(app)
        gui.wait_for_canvas()

        # Take screenshot for visual verification
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            screenshot_path = f.name
        try:
            gui.screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            assert os.path.exists(screenshot_path), "Screenshot file not created"
        finally:
            if os.path.exists(screenshot_path):
                os.unlink(screenshot_path)

        # Verify canvas is rendering
        canvas = gui.page.locator("canvas")
        assert canvas.is_visible(), "Canvas is not visible"

    def test_app_canvas_size(self):
        """Test that app canvas has reasonable dimensions."""
        app = self.get_test_app()
        gui = self.start_gui(app)
        gui.wait_for_canvas()

        width, height = gui.get_canvas_size()
        assert width > 0, f"Canvas width should be positive, got {width}"
        assert height > 0, f"Canvas height should be positive, got {height}"
        assert width >= 100, f"Canvas width seems too small: {width}"
        assert height >= 100, f"Canvas height seems too small: {height}"

    def test_server_running(self):
        """Test that server is running after start."""
        app = self.get_test_app()
        gui = self.start_gui(app)
        self.assert_server_running()


class TestXeyes(XpraGUITestCase):
    """Example tests for xeyes application."""

    @unittest.skipUnless(platform.system() == "Linux", "Linux only")
    def test_xeyes_opens(self):
        """Test that xeyes displays correctly."""
        gui = self.start_gui("xeyes")
        gui.wait_for_canvas()

        # Take screenshot for visual verification
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            screenshot_path = f.name
        try:
            gui.screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            assert os.path.exists(screenshot_path), "Screenshot file not created"
        finally:
            if os.path.exists(screenshot_path):
                os.unlink(screenshot_path)

        # Verify canvas is rendering
        canvas = gui.page.locator("canvas")
        assert canvas.is_visible(), "Canvas is not visible"

    def test_xeyes_canvas_size(self):
        """Test that xeyes canvas has reasonable dimensions."""
        gui = self.start_gui("xeyes")
        gui.wait_for_canvas()

        width, height = gui.get_canvas_size()
        assert width > 0, f"Canvas width should be positive, got {width}"
        assert height > 0, f"Canvas height should be positive, got {height}"
        assert width >= 100, f"Canvas width seems too small: {width}"
        assert height >= 100, f"Canvas height seems too small: {height}"

    def test_server_running(self):
        """Test that server is running after start."""
        gui = self.start_gui("xeyes")
        self.assert_server_running()


class TestXcalc(XpraGUITestCase):
    """Example tests for xcalc application."""

    @unittest.skipUnless(platform.system() == "Linux", "Linux only")

    def test_xcalc_opens(self):
        """Test that xcalc displays correctly."""
        gui = self.start_gui("xcalc")
        gui.wait_for_canvas()

        # Verify canvas is visible
        self.assert_canvas_visible()

    def test_xcalc_screenshot(self):
        """Test screenshot capture with xcalc."""
        gui = self.start_gui("xcalc", headless=False)
        gui.wait_for_canvas()

        screenshot_path = "/tmp/xcalc_test.png"
        try:
            gui.screenshot(screenshot_path)
            assert os.path.exists(screenshot_path), "Screenshot not created"
            assert os.path.getsize(screenshot_path) > 0, "Screenshot is empty"
        finally:
            if os.path.exists(screenshot_path):
                os.unlink(screenshot_path)


class TestXterm(XpraGUITestCase):
    """Example tests for xterm application."""

    @unittest.skipUnless(platform.system() == "Linux", "Linux only")

    def test_xterm_opens(self):
        """Test that xterm displays correctly."""
        # Use -e to run a simple command that exits
        gui = self.start_gui("xterm", extra_args=["--start-child=ls"])
        gui.wait_for_canvas()

        # Verify server is running
        self.assert_server_running()


class TestMultipleApps(XpraGUITestCase):
    """Example tests for managing multiple applications."""

    @unittest.skipUnless(platform.system() == "Linux", "Linux only")

    def test_sequential_apps(self):
        """Test starting multiple apps sequentially."""
        # First app
        gui1 = self.start_gui("xeyes")
        gui1.wait_for_canvas()
        self.assert_canvas_visible()

        # Clean up first app
        gui1.disconnect()
        self.server.stop()
        self.server = None
        self.client = None

        # Second app
        gui2 = self.start_gui("xcalc")
        gui2.wait_for_canvas()
        self.assert_canvas_visible()


class TestServerLogs(XpraGUITestCase):
    """Example tests for server log capture."""

    @unittest.skipUnless(platform.system() == "Linux", "Linux only")

    def test_log_capture(self):
        """Test that server logs are captured."""
        gui = self.start_gui("xeyes")
        gui.wait_for_canvas()

        logs = self.get_server_logs()
        # Logs should contain some output
        assert isinstance(logs, str), "Logs should be a string"

        # Depending on configuration, we might see various messages
        # For now, just verify we can get logs without error
        print(f"Captured {len(logs)} characters of logs")


class TestPytestStyle:
    """
    Example tests using pytest-style instead of unittest base class.

    These tests demonstrate the pytest fixture API.
    """

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_xeyes_with_fixtures(self, xpra_server):
        """Test xeyes using pytest fixtures."""
        import tempfile

        # Start server and connect
        ws_url = xpra_server.start("xeyes")
        from gui_no_kit import PlaywrightClient
        client = PlaywrightClient(ws_url, headless=True)
        client.connect()

        try:
            client.wait_for_canvas()

            # Take screenshot
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                screenshot_path = f.name
            client.screenshot(screenshot_path)

            assert os.path.exists(screenshot_path), "Screenshot not created"
            os.unlink(screenshot_path)

            # Verify server is running
            assert xpra_server.is_running(), "Server not running"
        finally:
            client.disconnect()

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_xcalc_with_gui_client_fixture(self, gui_client):
        """Test using the gui_client fixture."""
        client = gui_client.start_and_connect("xcalc")
        client.wait_for_canvas()

        # Verify canvas size
        width, height = client.get_canvas_size()
        assert width > 0 and height > 0

        gui_client.disconnect()


if __name__ == "__main__":
    # Run with unittest
    unittest.main()


class TestCrossPlatform(XpraGUITestCase):
    """
    Example tests demonstrating cross-platform support.

    These tests show how to write tests that work on different platforms.
    """

    @unittest.skipIf(platform.system() != "Linux", "Linux-only test")
    def test_linux_x11_app(self):
        """Test X11 application on Linux with Xvfb."""
        gui = self.start_gui("xeyes", use_xvfb=True)
        gui.wait_for_canvas()
        self.assert_canvas_visible()

    @unittest.skipIf(platform.system() != "Darwin", "macOS-only test")
    def test_macos_native_app(self):
        """Test native macOS application."""
        # Note: use_xvfb is ignored on macOS
        textedit_path = "/Applications/TextEdit.app/Contents/MacOS/TextEdit"
        if os.path.exists(textedit_path):
            gui = self.start_gui(textedit_path, use_xvfb=False)
            gui.wait_for_canvas()
            self.assert_canvas_visible()
        else:
            self.skipTest("TextEdit not found")

    @unittest.skipIf(platform.system() != "Windows", "Windows-only test")
    def test_windows_app(self):
        """Test Windows application."""
        # Note: use_xvfb is ignored on Windows
        gui = self.start_gui("notepad.exe", use_xvfb=False)
        gui.wait_for_canvas()
        self.assert_canvas_visible()

    def test_cross_platform_detection(self):
        """Test that platform detection works correctly."""
        import platform as pf
        current_platform = pf.system()

        # Verify platform is one of the supported ones
        assert current_platform in ("Linux", "Darwin", "Windows"), \
            f"Unsupported platform: {current_platform}"

        # On Linux, Xvfb can be used for headless operation
        if current_platform == "Linux":
            # This should work
            gui = self.start_gui("xeyes", use_xvfb=True)
            gui.wait_for_canvas()
        else:
            # On macOS and Windows, use_xvfb is ignored
            # (warning will be issued but test continues)
            try:
                gui = self.start_gui(
                    "xterm" if current_platform == "Linux" else "ls",
                    use_xvfb=True  # Will be ignored with warning
                )
            except Exception as e:
                # App might not exist, that's ok for this test
                if "xpra" not in str(e).lower():
                    self.skipTest(f"Test application not available: {e}")
                raise


class TestPlatformSpecificBehavior(unittest.TestCase):
    """Tests for platform-specific behavior."""

    def test_platform_detection(self):
        """Test that XpraServer correctly detects the platform."""
        from gui_no_kit import XpraServer

        server = XpraServer()
        expected_platform = platform.system()

        assert server.platform == expected_platform, \
            f"Expected platform {expected_platform}, got {server.platform}"

    @unittest.skipIf(platform.system() != "Linux", "Linux-only test")
    def test_linux_display_management(self):
        """Test that display management works on Linux."""
        from gui_no_kit import XpraServer

        server = XpraServer()

        # Should be able to find a free display on Linux
        try:
            display = server._find_free_display()
            assert display.startswith(":"), f"Invalid display format: {display}"
        except RuntimeError as e:
            self.skipTest(f"Cannot find display (non-X11 environment?): {e}")

    @unittest.skipIf(platform.system() == "Linux", "Non-Linux test")
    def test_non_linux_display_rejection(self):
        """Test that display management is rejected on non-Linux platforms."""
        from gui_no_kit import XpraServer

        server = XpraServer()

        # Should raise an error on non-Linux platforms
        with self.assertRaises(RuntimeError) as ctx:
            server._find_free_display()

        assert "only supported on Linux" in str(ctx.exception), \
            f"Expected Linux-specific error, got: {ctx.exception}"

    @unittest.skipIf(platform.system() == "Linux", "Non-Linux test")
    def test_non_linux_xvfb_rejection(self):
        """Test that Xvfb is rejected on non-Linux platforms."""
        from gui_no_kit import XpraServer

        server = XpraServer()

        # Should raise an error on non-Linux platforms
        with self.assertRaises(RuntimeError) as ctx:
            server._start_xvfb(":100")

        assert "only supported on Linux" in str(ctx.exception), \
            f"Expected Linux-specific error, got: {ctx.exception}"
