"""
Linux-specific example tests for gui-no-kit framework.

These tests are designed for Linux/X11 applications and require Xvfb for headless operation.
"""

import os
import tempfile
import unittest

from gui_no_kit import XpraGUITestCase


class TestXeyes(XpraGUITestCase):
    """Example tests for xeyes application."""

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


if __name__ == "__main__":
    # Run with unittest
    unittest.main()