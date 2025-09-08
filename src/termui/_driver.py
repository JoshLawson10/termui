import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from termui import events, messages

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
        self._cursor_origin: tuple[int, int] | None = None
        self._auto_restart: bool = True

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

    def enable_input(self) -> None:
        """Enable input for the terminal."""

    @abstractmethod
    def disable_input(self) -> None:
        """Disable input for the terminal."""

    def send_message(self, message: messages.Message) -> None:
        """Send a message to the target app.

        Args:
            message: A message.
        """
        coro = self._app.post_message(message)
        if coro is not None:
            asyncio.run_coroutine_threadsafe(coro, loop=self._loop)

    def process_message(self, message: messages.Message) -> None:
        """Perform additional processing on a message, prior to sending.

        Args:
            event: A message to process.
        """
        if self._cursor_origin is None:
            offset_x = 0
            offset_y = 0
        else:
            offset_x, offset_y = self._cursor_origin
        if isinstance(message, events.MouseEvent):
            message.x -= offset_x
            message.y -= offset_y

        if isinstance(message, events.MouseDown):
            if message.button:
                self._down_buttons.append(message.button)
        elif isinstance(message, events.MouseUp):
            if message.button and message.button in self._down_buttons:
                self._down_buttons.remove(message.button)
        elif isinstance(message, events.MouseMove):
            if (
                self._down_buttons
                and not message.button
                and self._last_move_event is not None
            ):
                # Deduplicate self._down_buttons while preserving order.
                buttons = list(dict.fromkeys(self._down_buttons).keys())
                self._down_buttons.clear()
                move_event = self._last_move_event
                for button in buttons:
                    self.send_message(
                        events.MouseUp(
                            message.widget,
                            move_event.x,
                            move_event.y,
                            button=button,
                        )
                    )
            self._last_move_event = message

        self.send_message(message)

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
