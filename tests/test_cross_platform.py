"""
Unit tests for cross-platform functionality.
"""

import unittest

from gui_no_kit import XpraGUITestCase


class TestCrossPlatform(XpraGUITestCase):
    """
    Unit tests demonstrating cross-platform support.
    """

    def test_cross_platform_detection(self):
        """Test that platform detection works correctly."""
        import platform as pf
        current_platform = pf.system()

        # Verify platform is one of the supported ones
        assert current_platform in ("Linux", "Darwin", "Windows"), \
            f"Unsupported platform: {current_platform}"


if __name__ == "__main__":
    # Run with unittest
    unittest.main()