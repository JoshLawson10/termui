from typing import Optional


class Logger:
    def __init__(
        self,
        log_file: Optional[str] = None,
        stdout: Optional[bool] = True,
        stderr: Optional[bool] = True,
    ) -> None:
        self.log_file = log_file
        self.stdout = stdout
        self.stderr = stderr

        if self.log_file:
            with open(self.log_file, "a") as f:
                f.seek(0)
                f.truncate()
                f.write(f"[TermUI Logger Initialized]\n")

    def system(self, message: str) -> None:
        if self.stdout:
            if self.log_file:
                with open(self.log_file, "a") as f:
                    f.write(f"[TermUI Log] {message}\n")
            else:
                print(f"[TermUI Log] {message}")

    def warning(self, message: str) -> None:
        if self.stdout:
            if self.log_file:
                with open(self.log_file, "a") as f:
                    f.write(f"[TermUI Warning] {message}\n")
            else:
                print(f"[TermUI Warning] {message}")

    def error(self, message: str | Exception) -> None:
        if self.stderr:
            if self.log_file:
                with open(self.log_file, "a") as f:
                    f.write(f"[TermUI Error] {message}\n")
            else:
                print(f"[TermUI Error] {message}")


class AlignmentError(Exception):
    """Base class for all alignment errors."""

    pass


class DimensionError(Exception):
    """Base class for all size-related errors."""

    pass


class AppError(Exception):
    """Base class for all application-related errors."""

    pass


class ScreenError(Exception):
    """Base class for all screen-related errors."""

    pass


class WidgetError(Exception):
    """Base class for all widget-related errors."""

    pass


class RenderError(Exception):
    """Base class for all rendering-related errors."""

    pass


class AsyncError(Exception):
    """Base class for all asynchronous operation errors."""

    pass
