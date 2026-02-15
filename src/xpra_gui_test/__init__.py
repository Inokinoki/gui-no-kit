"""
Xpra GUI Testing Framework

A framework for automated GUI testing of X11 applications using Xpra's HTML5 client
and Playwright browser automation.
"""

__version__ = "0.1.0"

from gui_no_kit.server import XpraServer
from gui_no_kit.client import PlaywrightClient
from gui_no_kit.test_case import XpraGUITestCase
from gui_no_kit.logs import LogCapture

__all__ = [
    "XpraServer",
    "PlaywrightClient",
    "XpraGUITestCase",
    "LogCapture",
]
