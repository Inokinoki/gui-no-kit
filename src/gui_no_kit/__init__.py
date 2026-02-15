"""
Xpra GUI Testing Framework

A framework for automated GUI testing of X11 applications using Xpra's HTML5 client
and Playwright browser automation.
"""

__version__ = "0.1.0"

from .server import XpraServer
from .client import PlaywrightClient
from .test_case import XpraGUITestCase
from .logs import LogCapture

__all__ = [
    "XpraServer",
    "PlaywrightClient",
    "XpraGUITestCase",
    "LogCapture",
]
