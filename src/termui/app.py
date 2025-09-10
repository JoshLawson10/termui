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
        self.driver = Driver()
        """The I/O driver for the application"""
        self.renderer = Renderer(self.driver)
        """The renderer for the application"""
        self._default_keybinds: list[Keybind] = [
            Keybind(key="q", action=self.quit, description="Quit the application"),
        ]
        """The default key bindings for all applications."""

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
        self.screens[screen.name] = screen

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
        if screen_name not in self.screens:
            raise ScreenError(
                f"Screen '{screen_name}' not found. Available screens: {list(self.screens.keys())}"
            )

        if self.current_screen is not None:
            self.current_screen.unmount()

        self.current_screen = self.screens[screen_name]
        self.current_screen.mount()
        self.driver.register_keybinds_from_object(self.current_screen)
        self.renderer.pipe(self.current_screen)

    async def _input_loop(self) -> None:
        """Run the input handler in an asynchronous loop.

        Continuously processes input events and forwards them to the current
        screen while the application is running.
        """
        while self._running:
            try:
                event = await self.driver.get_event()
                if self.current_screen and isinstance(event, events.InputEvent):
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
                    if self.screens:
                        self.show_screen(next(iter(self.screens)))
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

            # Create tasks that run concurrently
            input_task = asyncio.create_task(self._input_loop())
            update_task = asyncio.create_task(self._update_loop())
            render_task = asyncio.create_task(self._render_loop())

            # Wait for any task to complete (which shouldn't happen in normal operation)
            _, pending = await asyncio.wait(
                {input_task, update_task, render_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel remaining tasks
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
