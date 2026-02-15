"""Test that all package imports work correctly."""

import unittest


class TestImports(unittest.TestCase):
    """Test that all public APIs can be imported."""

    def test_import_server(self):
        """Test that XpraServer can be imported."""
        from gui_no_kit import XpraServer
        assert XpraServer is not None

    def test_import_client(self):
        """Test that PlaywrightClient can be imported."""
        from gui_no_kit import PlaywrightClient
        assert PlaywrightClient is not None

    def test_import_test_case(self):
        """Test that XpraGUITestCase can be imported."""
        from gui_no_kit import XpraGUITestCase
        assert XpraGUITestCase is not None

    def test_import_log_capture(self):
        """Test that LogCapture can be imported."""
        from gui_no_kit import LogCapture
        assert LogCapture is not None

    def test_import_all(self):
        """Test that __all__ is properly defined."""
        from gui_no_kit import __all__
        expected = ["XpraServer", "PlaywrightClient", "XpraGUITestCase", "LogCapture"]
        assert set(__all__) == set(expected)


class TestPackageStructure(unittest.TestCase):
    """Test that the package structure is correct."""

    def test_version_defined(self):
        """Test that __version__ is defined."""
        from gui_no_kit import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_module_has_docstring(self):
        """Test that the module has a docstring."""
        import gui_no_kit
        assert gui_no_kit.__doc__ is not None
        assert len(gui_no_kit.__doc__) > 0


if __name__ == "__main__":
    unittest.main()
