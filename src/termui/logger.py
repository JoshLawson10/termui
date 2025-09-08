import os
from typing import Optional


class Logger:
    """Simple logging utility for terminal UI applications.

    Provides basic logging functionality with support for file output
    and different log levels (system, warning, error).
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        stdout: Optional[bool] = True,
        stderr: Optional[bool] = True,
    ) -> None:
        """Initialize the logger with output configuration.

        Args:
            log_file: Path to the log file. If provided, creates the directory
                     structure if it doesn't exist and truncates the file.
            stdout: Whether to enable stdout logging for system and warning messages.
            stderr: Whether to enable stderr logging for error messages.
        """
        self.log_file = log_file
        """Path to the log file."""
        self.stdout = stdout
        """Whether to enable stdout logging."""
        self.stderr = stderr
        """Whether to enable stderr logging."""

        if self.log_file:
            if not os.path.exists(os.path.dirname(self.log_file)):
                os.makedirs(os.path.dirname(self.log_file))
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.seek(0)
                f.truncate()
                f.write("[TermUI Logger Initialized]\n")

    def _write_to_file(self, message: str) -> None:
        """Write a log message to the log file.

        Args:
            message: The message to log.
        """
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{message}\n")
        else:
            print(message)

    def system(self, message: str) -> None:
        """Log a system message.

        Args:
            message: The message to log with a "[Log]" prefix.
        """
        if self.stdout:
            self._write_to_file(f"[Log] {message}")

    def debug(self, message: str) -> None:
        """Log a debug message.

        Args:
            message: The message to log with a "[Debug]" prefix.
        """
        if self.stdout:
            self._write_to_file(f"[Debug] {message}")

    def warning(self, message: str) -> None:
        """Log a warning message.

        Args:
            message: The warning message to log with a "[Warning]" prefix.
        """
        if self.stdout:
            self._write_to_file(f"[Warning] {message}")

    def error(self, message: str | Exception) -> None:
        """Log an error message.

        Args:
            message: The error message or exception to log with a "[Error]" prefix.
        """
        if self.stderr:
            self._write_to_file(f"[Error] {message}")


log = Logger("logs/log.txt")
