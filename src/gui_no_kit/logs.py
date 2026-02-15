"""
Non-blocking log capture for subprocess output.

Captures stdout and stderr from subprocesses in separate threads
to avoid blocking during test execution.
"""

import threading
from typing import TextIO, List


class LogCapture:
    """
    Captures stdout and stderr from a subprocess in non-blocking mode.

    Uses separate threads to read from process streams, ensuring that
    the main thread is not blocked during log capture.
    """

    def __init__(self) -> None:
        self.stdout_thread: threading.Thread | None = None
        self.stderr_thread: threading.Thread | None = None
        self.buffer: List[str] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def attach(self, process: "subprocess.Popen[str]") -> None:
        """
        Start capturing output from the given process.

        Args:
            process: subprocess.Popen instance with stdout and stderr pipes
        """
        if process.stdout is None or process.stderr is None:
            raise ValueError("Process must have stdout and stderr set to PIPE")

        self._stop_event.clear()

        self.stdout_thread = threading.Thread(
            target=self._read_stream,
            args=(process.stdout, "STDOUT"),
            daemon=True,
        )
        self.stderr_thread = threading.Thread(
            target=self._read_stream,
            args=(process.stderr, "STDERR"),
            daemon=True,
        )

        self.stdout_thread.start()
        self.stderr_thread.start()

    def stop(self) -> None:
        """Signal threads to stop and wait for them to finish."""
        self._stop_event.set()
        if self.stdout_thread:
            self.stdout_thread.join(timeout=2)
        if self.stderr_thread:
            self.stderr_thread.join(timeout=2)

    def get_output(self) -> str:
        """
        Get all captured output as a single string.

        Returns:
            Combined stdout and stderr output with prefixes
        """
        with self._lock:
            return "\n".join(self.buffer)

    def get_lines(self) -> List[str]:
        """
        Get captured output as a list of lines.

        Returns:
            List of log lines with prefixes
        """
        with self._lock:
            return list(self.buffer)

    def clear(self) -> None:
        """Clear the captured log buffer."""
        with self._lock:
            self.buffer.clear()

    def _read_stream(self, stream: TextIO, prefix: str) -> None:
        """
        Read lines from a stream in a separate thread.

        Args:
            stream: File-like object to read from
            prefix: Prefix to add to each line (e.g., "STDOUT" or "STDERR")
        """
        for line in iter(stream.readline, ""):
            if not line:
                break
            decoded = line.rstrip("\n\r")
            with self._lock:
                self.buffer.append(f"[{prefix}] {decoded}")
            if self._stop_event.is_set():
                break
