"""This is the base class for all TermUI applications"""

import asyncio
import inspect
import os
import sys
import termios
import traceback
import tty
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from termui._context_manager import (
    _app,
    _input_handler,
    _logger,
    _renderer,
    input_handler,
    log,
    renderer,
)

from termui.cursor import Cursor
from termui.errors import AsyncError, ScreenError
from termui.input import InputHandler, Keybind
from termui.input.driver import Driver
from termui.logger import Logger
from termui.message import Message
from termui.renderer import Renderer
from termui.screen import Screen

if TYPE_CHECKING:
    from termui._driver import Driver as DriverType


class App(ABC):
    """The base class for all TermUI applications."""

    def __init__(self) -> None:
        """Initialize the application with default settings."""
        self.screens: dict[str, Screen] = {}
        """A stack of screens registered to the current app"""
        self.current_screen: Optional[Screen] = None
        """The currently rendered screen"""
        self._running = True
        """Whether the app is running"""
        self._default_keybinds: list[Keybind] = [
            Keybind(key="q", action=self.quit, description="Quit the application"),
        ]
        """The default key bindings for all applications."""
        self.driver: DriverType = Driver(self)
        """The driver instance for handling input and output."""

        _renderer.set(Renderer())
        _input_handler.set(InputHandler())
        _logger.set(Logger("logs/log.txt"))

        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)

        _app.set(self)

    def _register_decorated_keybinds(self) -> None:
        """Find and register all methods decorated with @keybind.

        Scans all methods of the app instance for keybind decorations and
        registers them with the input handler, along with default keybinds.
        """
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            info = getattr(method, "_keybind_info", None)
            if info is not None:
                keybind_obj = Keybind(
                    key=info["key"],
                    action=method,
                    description=info["description"],
                    visible=info["visible"],
                )
                input_handler.register_keybind(keybind_obj)

        for keybind in self._default_keybinds:
            input_handler.register_keybind(keybind)

    @property
    def log(self):
        """Get the application's logger."""
        return log

    def register_screen(self, screen: Screen) -> None:
        """Register a new screen with the application.

        Args:
            screen: The screen instance to register.

        Raises:
            ScreenError: If the provided object is not a Screen instance.
        """
        if not isinstance(screen, Screen):
            raise ScreenError("Expected a Screen instance.")
        screen.setup()
        self.screens[screen.name] = screen

    @abstractmethod
    def build(self) -> None:
        """Setup the application with initial screens.

        This method is intended to be overridden by the inheriting class."""
        raise NotImplementedError("Subclasses must implement the build method.")

    def show_screen(self, screen_name: str) -> None:
        """Switch to a different screen by name.

        Args:
            screen_name: The name of the screen to switch to.

        Raises:
            ScreenError: If the screen name is not found in registered screens.
        """
        if screen_name not in self.screens:
            raise ScreenError(
                f"Screen '{screen_name}' not found. "
                f"Available screens: {list(self.screens.keys())}"
            )

        if self.current_screen is not None:
            self.current_screen.unmount()

        self.current_screen = self.screens[screen_name]
        self.current_screen.mount()

    async def _input_loop(self) -> None:
        """Run the input handler in an asynchronous loop.

        Continuously processes input events and forwards them to the current
        screen while the application is running.
        """
        while self._running:
            event = await input_handler.process_input()
            if self.current_screen and event:
                self.current_screen.handle_input_event(event)

            await asyncio.sleep(0.001)

    async def _update_loop(self) -> None:
        """Run the update loop for the current screen.

        Continuously calls the update method on the current screen while
        the application is running.
        """
        while self._running:
            if self.current_screen:
                self.current_screen.update()

            await asyncio.sleep(0.001)

    async def _render_loop(self) -> None:
        """Run the renderer in an asynchronous loop.

        Continuously renders the current screen while the application is
        running. If no current screen is set, defaults to the first screen.
        """
        while self._running:
            if not self.current_screen:
                self.show_screen(next(iter(self.screens)))

            renderer.render()
            await asyncio.sleep(0.001)

    async def _run_async(self) -> None:
        """Run the application asynchronously.

        Sets up the application, registers keybinds, enables mouse input,
        and starts the main application loops (input, update, render).

        Raises:
            AsyncError: If the application loop is cancelled.
        """
        self.build()
        self._register_decorated_keybinds()
        self._running = True
        input_handler.enable_mouse()

        try:
            await asyncio.gather(
                self._input_loop(),
                self._update_loop(),
                self._render_loop(),
            )
        except KeyboardInterrupt:
            self._running = False
            self.quit()
        except asyncio.CancelledError as e:
            raise AsyncError("Application loop was cancelled.") from e
        except Exception:
            log.error(traceback.format_exc())
            self._running = False
            self.quit()
        finally:
            if self.current_screen:
                self.current_screen.unmount()
            input_handler.stop()
            self._running = False
            self.quit()

    def run(self) -> None:
        """Run the application synchronously.

        A convenience method that wraps run_async() with asyncio.run().
        Handles keyboard interrupts and other exceptions gracefully.
        """
        try:
            # Set the current application context
            _app.set(self)

            self.old_settings = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            self._running = False
            self.quit()
        except Exception:
            log.error(traceback.format_exc())
            self._running = False
            self.quit()
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
            sys.stdout.write("\033[?1003l\033[?1006l")
            sys.stdout.flush()

    def quit(self) -> None:
        """Safely handle application termination."""
        input_handler.stop()
        renderer.clear()
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        sys.stdout.write("\033[?1003l\033[?1006l")
        sys.stdout.flush()
        Cursor.show()
        os._exit(0)

    def post_message(self, message: Message) -> None:
        """Process a message received from the input handler."""
