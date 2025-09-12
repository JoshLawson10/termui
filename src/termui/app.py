"""This is the base class for all TermUI applications"""

import asyncio
import os
import traceback
from abc import ABC, abstractmethod
from typing import Optional

from termui import events
from termui._context_manager import _app
from termui.drivers import Driver
from termui.errors import AsyncError, ScreenError
from termui.keybind import Keybind
from termui.logger import log as _log
from termui.renderer import Renderer
from termui.screen import Screen
from termui.widget import Widget


class App(ABC):
    """The base class for all TermUI applications."""

    def __init__(self) -> None:
        """Initialize the application with default settings."""
        self.screen_stack: dict[str, Screen] = {}
        """A stack of screens registered to the current app"""
        self.current_screen: Optional[Screen] = None
        """The currently rendered screen"""

        self._running = True
        """Whether the app is running"""

        self.driver = Driver()
        """The I/O driver for the application"""
        self.renderer = Renderer(self.driver)
        """The renderer for the application"""
        self._default_keybinds: list[Keybind] = [
            Keybind(key="q", action=self.quit, description="Quit the application"),
        ]
        """The default key bindings for all applications."""

        self._previous_mouse_position: tuple[int, int] = (-1, -1)
        self.mouse_position: tuple[int, int] = (0, 0)
        """The current mouse position."""

        self._previous_mouse_over: Widget | None = None
        self.mouse_over: Widget | None = None
        """The widget the mouse is currently over."""
        self._mouse_down_widget: Widget | None = None
        """The widget the mouse is currently down."""

        _app.set(self)

    @property
    def log(self):
        """Expose the TermUI logger to the App."""
        return _log

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
        self.screen_stack[screen.name] = screen

    @abstractmethod
    def build(self) -> None:
        """Set up the application with initial screens.

        This method is intended to be overridden by the inheriting class."""
        raise NotImplementedError("Subclasses must implement the build method.")

    def show_screen(self, screen_name: str) -> None:
        """Switch to a different screen by name.

        Args:
            screen_name: The name of the screen to switch to.

        Raises:
            ScreenError: If the screen name is not found in registered screens.
        """
        if screen_name not in self.screen_stack:
            raise ScreenError(
                f"Screen '{screen_name}' not found. Available screens: {list(self.screen_stack.keys())}"
            )

        if self.current_screen is not None:
            self.current_screen.unmount()

        self.current_screen = self.screen_stack[screen_name]
        self.current_screen.mount()
        self.driver.register_keybinds_from_object(self.current_screen)
        self.renderer.pipe(self.current_screen)

    def _set_mouse_over(self, widget: Widget | None) -> None:
        """Called when the mouse is over another widget.

        Args:
            widget: The widget the mouse is currently over, or None for no widgets.
        """
        self.log.debug(f"Setting mouse over for widget {widget}")
        if widget is None:
            if self.mouse_over is not None:
                try:
                    self.mouse_over.handle_event(events.MouseExit())
                finally:
                    self.mouse_over = None
        else:
            if self.mouse_over is not widget:
                try:
                    if self.mouse_over is not None:
                        self.mouse_over.handle_event(events.MouseExit())
                    if widget is not None:
                        widget.handle_event(events.MouseEnter())
                finally:
                    self.mouse_over = widget

    def _update_mouse_over(self, screen: Screen) -> None:
        """Updates the mouse over after the next refresh.

        This method is called whenever a widget is added or removed, which may change
        the widget under the mouse.

        Args:
            screen: The screen to update the mouse over.
        """
        widget = screen.get_widget_at(*self.mouse_position)
        self._set_mouse_over(widget)

    async def _input_loop(self) -> None:
        """Run the input handler in an asynchronous loop.

        Continuously processes input events and forwards them to the current
        screen while the application is running.
        """
        while self._running:
            try:
                event = await self.driver.get_event()
                if self.current_screen and isinstance(event, events.InputEvent):
                    if isinstance(event, events.MouseMove):
                        self._previous_mouse_position = self.mouse_position
                        self.mouse_position = (int(event.x), int(event.y))
                        self._update_mouse_over(self.current_screen)
                    self.current_screen.handle_input_event(event)
            except Exception:
                self.log.error(f"Error in input loop: {traceback.format_exc()}")

            await asyncio.sleep(0.001)

    async def _update_loop(self) -> None:
        """Run the update loop for the current screen.

        Continuously calls the update method on the current screen while
        the application is running.
        """
        while self._running:
            try:
                if self.current_screen:
                    self.current_screen.update()
            except Exception:
                self.log.error(f"Error in update loop: {traceback.format_exc()}")

            await asyncio.sleep(0.016)  # ~60 FPS

    async def _render_loop(self) -> None:
        """Run the renderer in an asynchronous loop.

        Continuously renders the current screen while the application is
        running. If no current screen is set, defaults to the first screen.
        """
        while self._running:
            try:
                if not self.current_screen:
                    if self.screen_stack:
                        self.show_screen(next(iter(self.screen_stack)))
                    else:
                        await asyncio.sleep(0.1)
                        continue

                self.renderer.render()
            except Exception:
                self.log.error(f"Error in render loop: {traceback.format_exc()}")

            await asyncio.sleep(0.016)  # ~60 FPS

    async def _run_async(self) -> None:
        """Run the application asynchronously.

        Sets up the application, registers keybinds, enables mouse input,
        and starts the main application loops (input, update, render).

        Raises:
            AsyncError: If the application loop is cancelled.
        """
        try:
            self.build()
            self.driver.start()
            for kb in self._default_keybinds:
                self.driver.register_keybind(kb)
            self.driver.register_keybinds_from_object(self)
            self._running = True

            input_task = asyncio.create_task(self._input_loop())
            update_task = asyncio.create_task(self._update_loop())
            render_task = asyncio.create_task(self._render_loop())

            _, pending = await asyncio.wait(
                {input_task, update_task, render_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        except KeyboardInterrupt:
            self.quit()
        except asyncio.CancelledError as e:
            raise AsyncError("Application loop was cancelled.") from e
        except Exception:
            self.log.error(traceback.format_exc())
            self.quit()
        finally:
            self.quit()

    def run(self) -> None:
        """Run the application synchronously.

        A convenience method that wraps run_async() with asyncio.run().
        Handles keyboard interrupts and other exceptions gracefully.
        """
        try:
            # Set the current application context
            _app.set(self)
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            self.quit()
        except Exception:
            self.log.error(traceback.format_exc())
            self.quit()
        finally:
            self.quit()

    def quit(self) -> None:
        """Safely handle application termination."""
        self._running = False
        self.driver.stop()
        os._exit(0)
