"""
Xpra server lifecycle management for GUI testing.

Manages starting and stopping Xpra servers with WebSocket binding
for HTML5 client connections.

Supports multiple platforms:
- Linux/X11: X11 forwarding with optional Xvfb
- macOS: Native Cocoa display forwarding
- Windows: Windows GDI/desktop forwarding
"""

import os
import platform
import socket
import subprocess
import tempfile
import time
from typing import List

from .logs import LogCapture


class XpraServer:
    """
    Manages an Xpra server instance for GUI testing.

    Handles server startup with WebSocket binding, display management,
    and log capture for debugging test failures.

    Platform support:
    - Linux/X11: Uses X11 displays, optionally with Xvfb for headless operation
    - macOS: Uses native macOS display (Cocoa backend)
    - Windows: Uses Windows desktop (GDI backend)
    """

    def __init__(self, host: str = "127.0.0.1", port: int | None = None) -> None:
        """
        Initialize Xpra server manager.

        Args:
            host: Host to bind WebSocket server to
            port: Port for WebSocket (auto-assign if None)
        """
        self.host = host
        self.port = port or self._get_free_port()
        self.display: str | None = None
        self.process: subprocess.Popen[str] | None = None
        self.log_capture = LogCapture()
        self.xvfb_process: subprocess.Popen[str] | None = None
        self.platform = platform.system()  # 'Linux', 'Darwin', 'Windows'

    def start(
        self,
        app_command: str,
        extra_args: List[str] | None = None,
        use_xvfb: bool = True,
    ) -> str:
        """
        Start Xpra server with the specified application.

        Args:
            app_command: Command to start (e.g., "xeyes", "xcalc", "notepad.exe")
            extra_args: Additional arguments to pass to xpra
            use_xvfb: Whether to start Xvfb for virtual display (Linux/X11 only)

        Returns:
            WebSocket URL for connecting to the server
        """
        if self.process:
            raise RuntimeError("Server already running")

        # Platform-specific display setup
        # On Linux/X11, we can use Xvfb for headless operation
        # On macOS and Windows, Xpra uses the native display system
        if self.platform == "Linux" and use_xvfb:
            self.display = self._find_free_display()
            self.xvfb_process = self._start_xvfb(self.display)
            time.sleep(1)  # Give Xvfb time to start
        elif self.platform in ("Darwin", "Windows"):
            # macOS and Windows use native display - no Xvfb needed
            if use_xvfb:
                import warnings
                warnings.warn(
                    f"use_xvfb=True is ignored on {self.platform} "
                    "(native display is used instead)"
                )
        # For Linux without Xvfb, DISPLAY will be auto-detected by Xpra

        # Build xpra command
        args = [
            "xpra",
            "seamless",
            f"--start={app_command}",
            f"--bind-ws={self.host}:{self.port}",
            "--no-daemon",  # Keep in foreground for log capture
            "--speaker=no",
            "--microphone=no",
        ]

        if self.display:
            args.append(f"--display={self.display}")

        if extra_args:
            args.extend(extra_args)

        # Set up environment
        env = os.environ.copy()
        env["XPRA_LOG_DIR"] = tempfile.gettempdir()
        env["XPRA_NOTTY"] = "1"

        # Start the process
        self.process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Attach log capture
        self.log_capture.attach(self.process)

        # Wait for WebSocket to be ready
        self._wait_for_socket()

        return f"ws://{self.host}:{self.port}/"

    def stop(self, timeout: int = 10) -> None:
        """
        Stop the Xpra server.

        Args:
            timeout: Maximum time to wait for graceful shutdown
        """
        # Stop log capture
        self.log_capture.stop()

        # Terminate server process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None

        # Stop Xvfb if we started it
        if self.xvfb_process:
            try:
                self.xvfb_process.terminate()
                self.xvfb_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.xvfb_process.kill()
                self.xvfb_process.wait()
            self.xvfb_process = None

    def get_logs(self) -> str:
        """
        Get captured server logs.

        Returns:
            All captured stdout and stderr output
        """
        return self.log_capture.get_output()

    def is_running(self) -> bool:
        """
        Check if the server process is still running.

        Returns:
            True if server is running, False otherwise
        """
        return self.process is not None and self.process.poll() is None

    def _get_free_port(self) -> int:
        """Find a free TCP port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    def _find_free_display(self) -> str:
        """
        Find a free X11 display number (Linux/X11 only).

        Returns:
            Display string (e.g., ":100")

        Raises:
            RuntimeError: If on unsupported platform or no free display found
        """
        if self.platform != "Linux":
            raise RuntimeError(
                f"Display management is only supported on Linux/X11, "
                f"not on {self.platform}. "
                f"On macOS and Windows, Xpra uses the native display system."
            )

        # Check X11 socket directory
        x11_socket_dir = "/tmp/.X11-unix"
        used_displays = set()

        if os.path.exists(x11_socket_dir):
            for filename in os.listdir(x11_socket_dir):
                if filename.startswith("X"):
                    try:
                        display_num = int(filename[1:])
                        used_displays.add(display_num)
                    except ValueError:
                        continue

        # Find a free display starting from 100
        for display_num in range(100, 10000):
            if display_num not in used_displays:
                socket_path = os.path.join(x11_socket_dir, f"X{display_num}")
                if not os.path.exists(socket_path):
                    return f":{display_num}"

        raise RuntimeError("Could not find free X11 display")

    def _start_xvfb(self, display: str) -> subprocess.Popen[str]:
        """
        Start Xvfb for the given display (Linux/X11 only).

        Args:
            display: X11 display string (e.g., ":100")

        Returns:
            Xvfb process

        Raises:
            RuntimeError: If on unsupported platform or Xvfb fails to start
        """
        if self.platform != "Linux":
            raise RuntimeError(
                f"Xvfb is only supported on Linux/X11, not on {self.platform}. "
                f"On macOS and Windows, Xpra uses the native display system."
            )

        cmd = [
            "Xvfb",
            display,
            "-screen", "0", "1280x1024x24",
            "-ac",
            "-noreset",
        ]

        with open(os.devnull, 'w') as devnull:
            process = subprocess.Popen(
                cmd,
                stdout=devnull,
                stderr=devnull,
            )

        # Wait a bit for Xvfb to start
        time.sleep(0.5)

        if process.poll() is not None:
            raise RuntimeError(f"Xvfb failed to start on {display}")

        return process

    def _wait_for_socket(self, timeout: int = 10) -> None:
        """
        Wait for the WebSocket endpoint to be ready.

        Args:
            timeout: Maximum time to wait in seconds
        """
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((self.host, self.port))
                    if result == 0:
                        return
            except OSError:
                pass
            time.sleep(0.2)

        raise RuntimeError(
            f"WebSocket endpoint not ready after {timeout} seconds"
        )
