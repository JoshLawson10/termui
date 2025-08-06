import asyncio
import inspect
import os
import traceback
from abc import ABC, abstractmethod
from typing import Optional

from termui.errors import AsyncError, ScreenError
from termui.input import InputHandler, Keybind
from termui.logger import Logger
from termui.renderer import Renderer
from termui.screen import Screen


class App(ABC):
    def __init__(self) -> None:
        self.screens: dict[str, Screen] = {}
        self.current_screen: Optional[Screen] = None
        self.input_handler = InputHandler()
        self.renderer = Renderer(self)
        self._running = True
        self._default_keybinds: list[Keybind] = [
            Keybind(key="q", action=self.quit, description="Quit the application"),
        ]
        self._logger = Logger("logs/log.txt")

    @property
    def log(self) -> Logger:
        """Logger instance for the application."""
        return self._logger

    def _register_decorated_keybinds(self):
        """Finds and registers all methods decorated with @keybind."""
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            info = getattr(method, "_keybind_info", None)
            if info is not None:
                keybind_obj = Keybind(
                    key=info["key"],
                    action=method,
                    description=info["description"],
                    visible=info["visible"],
                )
                self.input_handler.register_keybind(keybind_obj)

        for keybind in self._default_keybinds:
            self.input_handler.register_keybind(keybind)

    def register_screen(self, screen: Screen) -> None:
        """Register a new screen."""
        if not isinstance(screen, Screen):
            raise ScreenError("Expected a Screen instance.")
        screen.setup()
        self.screens[screen.name] = screen

    @abstractmethod
    def build(self) -> None:
        """Setup the application with initial screens.

        This method is intended to be overridden by the inheriting class."""
        pass

    def show_screen(self, screen_name: str) -> None:
        """Switch to a different screen by name."""
        if screen_name not in self.screens:
            raise ScreenError(
                f"Screen '{screen_name}' not found. \n Available screens: {list(self.screens.keys())}"
            )

        if self.current_screen is not None:
            self.current_screen.unmount()

        self.current_screen = self.screens[screen_name]
        self.current_screen.mount(self)

    async def _input_loop(self):
        """Run the input handler in an asynchronous loop."""
        while self._running:
            self.input_handler.process_input()
            await asyncio.sleep(0.001)

    async def _update_loop(self):
        """Run the update loop for the current screen."""
        while self._running:
            if self.current_screen:
                self.current_screen.update()
            await asyncio.sleep(0.001)

    async def _render_loop(self):
        """Run the renderer in an asynchronous loop."""
        while self._running:
            if not self.current_screen:
                self.current_screen = self.screens[next(iter(self.screens))]
                self.current_screen.mount(self)

            self.renderer.render()
            await asyncio.sleep(0.001)

    async def run_async(self) -> None:
        """Run the application asynchronously."""
        self.build()
        self._register_decorated_keybinds()
        self._running = True

        try:
            await asyncio.gather(
                self._input_loop(),
                self._update_loop(),
                self._render_loop(),
            )
        except KeyboardInterrupt:
            self._running = False
            self.quit()
        except asyncio.CancelledError:
            raise AsyncError("Application loop was cancelled.")
        except Exception:
            self.log.error(traceback.format_exc())
            self._running = False
            self.quit()
        finally:
            if self.current_screen:
                self.current_screen.unmount()
            self.input_handler.stop()
            self._running = False
            self.quit()

    def run(self) -> None:
        """Run the application."""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            self._running = False
            self.quit()
        except Exception:
            self.log.error(traceback.format_exc())
            self._running = False
            self.quit()

    def quit(self) -> None:
        self.input_handler.stop()
        os._exit(0)
