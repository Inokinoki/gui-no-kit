"""
macOS-specific example tests for gui-no-kit framework.

These tests are designed for macOS applications using Xpra's Cocoa backend.
"""

import os
import unittest

from gui_no_kit import XpraGUITestCase


class TestMacOS(XpraGUITestCase):
    """
    Example tests demonstrating macOS-specific GUI testing.
    """

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


if __name__ == "__main__":
    # Run with unittest
    unittest.main()