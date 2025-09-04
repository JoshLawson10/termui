import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from termui import events

if TYPE_CHECKING:
    from termui.app import App


class Driver(ABC):
    """Base class for all input drivers."""

    def __init__(
        self,
        app: "App",
        *,
        debug: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
    ) -> None:
        """Initialize a driver.

        Args:
            app: The App instance.
            debug: Enable debug mode.
            mouse: Enable mouse support,
            size: Initial size of the terminal or `None` to detect.
        """
        self._app = app
        self._debug = debug
        self._mouse = mouse
        self._size = size
        self._loop = asyncio.get_running_loop()
        self._down_buttons: list[int] = []
        self._last_move_event: events.MouseMove | None = None

    @property
    def inline(self) -> bool:
        """Whether the driver is running in inline mode."""
        return True

    @abstractmethod
    def write(self, data: str) -> None:
        """Write data to the terminal."""

    def flush(self) -> None:
        """Flush the terminal output."""

    @abstractmethod
    def start_application_mode(self) -> None:
        """Start application mode."""

    @abstractmethod
    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""

    def suspend_application_mode(self) -> None:
        """Suspend application mode.

        Used to suspend application mode and allow uninhibited access to the terminal.
        """
        self.stop_application_mode()
        self.close()

    def resume_application_mode(self) -> None:
        """Resume application mode.

        Used to resume application mode after it has been previously suspended.
        """
        self.start_application_mode()

    @abstractmethod
    def enable_input(self) -> None:
        """Enable input for the terminal."""

    @abstractmethod
    def disable_input(self) -> None:
        """Disable input for the terminal."""

    @abstractmethod
    def close(self) -> None:
        """Close the terminal."""

    @abstractmethod
    def _enable_mouse_support(self) -> None:
        """Enable mouse support for the terminal."""

    @abstractmethod
    def _disable_mouse_support(self) -> None:
        """Disable mouse support for the terminal."""

    @abstractmethod
    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode for the terminal."""

    @abstractmethod
    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode for the terminal."""
