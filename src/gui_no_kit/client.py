"""
Playwright browser automation for Xpra HTML5 client.

Wraps Playwright to control the browser and interact with the
Xpra HTML5 client's canvas rendering of GUI applications.
"""

from typing import Any


class PlaywrightClient:
    """
    Manages Playwright browser for interacting with Xpra HTML5 client.

    Provides methods for connecting to the HTML5 client, taking screenshots,
    and simulating user interactions.
    """

    def __init__(self, ws_url: str, headless: bool = True) -> None:
        """
        Initialize Playwright client.

        Args:
            ws_url: WebSocket URL for Xpra server
            headless: Whether to run browser in headless mode
        """
        self.ws_url = ws_url
        self.headless = headless
        self.playwright: Any = None
        self.browser: Any = None
        self.page: Any = None
        self._connected = False

    def connect(self) -> None:
        """
        Launch browser and navigate to HTML5 client.

        Raises:
            RuntimeError: If already connected
            ImportError: If playwright is not installed
        """
        if self._connected:
            raise RuntimeError("Already connected")

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise ImportError(
                "playwright is required. Install with: pip install playwright"
            ) from e

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()

        # Navigate to HTML5 client with WebSocket URL parameter
        # The HTML5 client should auto-connect when provided with the URL
        url = f"http://{self.ws_url.replace('ws://', '')}?connect={self.ws_url}"
        self.page.goto(url)

        # Wait for the Xpra canvas to be ready
        self._wait_for_canvas()

        self._connected = True

    def disconnect(self) -> None:
        """Close browser and cleanup resources."""
        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        self.page = None
        self._connected = False

    def screenshot(self, path: str) -> None:
        """
        Save a screenshot of the current canvas state.

        Args:
            path: File path to save screenshot

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.page:
            raise RuntimeError("Not connected")

        canvas = self.page.locator("canvas").first
        canvas.screenshot(path=path)

    def click(self, selector: str, timeout: int = 5000) -> None:
        """
        Click an element on the page.

        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait for element

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.page:
            raise RuntimeError("Not connected")

        self.page.click(selector, timeout=timeout)

    def click_canvas_at(self, x: int, y: int) -> None:
        """
        Click on the canvas at specific coordinates.

        Args:
            x: X coordinate relative to canvas
            y: Y coordinate relative to canvas

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.page:
            raise RuntimeError("Not connected")

        canvas = self.page.locator("canvas").first
        canvas.click(button="left", position={"x": x, "y": y})

    def wait_for_element(self, selector: str, timeout: int = 5000) -> Any:
        """
        Wait for an element to appear on the page.

        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in milliseconds

        Returns:
            The element handle

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.page:
            raise RuntimeError("Not connected")

        return self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_canvas(self, timeout: int = 10000) -> None:
        """
        Wait for the Xpra canvas to be ready.

        Args:
            timeout: Maximum time to wait in milliseconds

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.page:
            raise RuntimeError("Not connected")

        self._wait_for_canvas(timeout=timeout)

    def get_canvas_size(self) -> tuple[int, int]:
        """
        Get the dimensions of the Xpra canvas.

        Returns:
            Tuple of (width, height)

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.page:
            raise RuntimeError("Not connected")

        canvas = self.page.locator("canvas").first
        width = canvas.evaluate("el => el.width")
        height = canvas.evaluate("el => el.height")
        return (width, height)

    def execute_script(self, script: str, *args: Any) -> Any:
        """
        Execute JavaScript in the browser context.

        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script

        Returns:
            Result of script execution

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.page:
            raise RuntimeError("Not connected")

        return self.page.evaluate(script, *args)

    def is_connected(self) -> bool:
        """
        Check if the client is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._connected

    def _wait_for_canvas(self, timeout: int = 10000) -> None:
        """
        Internal method to wait for Xpra canvas to be ready.

        Args:
            timeout: Maximum time to wait in milliseconds

        Raises:
            RuntimeError: If canvas does not appear
        """
        # Try multiple possible canvas selectors
        selectors = [
            "canvas[keyboard='true']",
            "canvas[keyboard=true]",
            "canvas.xpra-canvas",
            "#xpra-canvas",
            "canvas",
        ]

        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, timeout=timeout)
                return
            except Exception:
                continue

        raise RuntimeError(
            f"Xpra canvas not found after {timeout}ms"
        )

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.disconnect()
