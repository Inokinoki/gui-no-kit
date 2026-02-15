"""
Integration tests for basic GUI application testing across platforms.
"""

import os
import platform
import tempfile
import unittest

from gui_no_kit import XpraGUITestCase


class TestBasicApp(XpraGUITestCase):
    """Integration tests for basic applications on each platform."""

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


if __name__ == "__main__":
    # Run with unittest
    unittest.main()