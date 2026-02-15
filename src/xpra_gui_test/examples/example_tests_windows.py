"""
Windows-specific example tests for gui-no-kit framework.

These tests are designed for Windows applications using Xpra's GDI backend.
"""

import unittest

from gui_no_kit import XpraGUITestCase


class TestWindows(XpraGUITestCase):
    """
    Example tests demonstrating Windows-specific GUI testing.
    """

    def test_windows_native_app(self):
        """Test native Windows application."""
        # Note: use_xvfb is ignored on Windows
        gui = self.start_gui("notepad.exe", use_xvfb=False)
        gui.wait_for_canvas()
        self.assert_canvas_visible()


if __name__ == "__main__":
    # Run with unittest
    unittest.main()