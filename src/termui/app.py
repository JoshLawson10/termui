from abc import ABC, abstractmethod
import inspect
import asyncio
from typing import Optional

from termui.screen import Screen
from termui.input import InputHandler, Keybind
from termui.renderer import Renderer


class App(ABC):
    def __init__(self) -> None:
        self.screens: dict[str, Screen] = {}
        self.current_screen: Optional[Screen] = None
        self.input_handler = InputHandler()
        self.renderer = Renderer()
        self._running = False
        self._frame_rate = 60
        self._frame_time = 1.0 / self._frame_rate

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

    def register_screen(self, screen: Screen) -> None:
        """Register a new screen."""
        if not isinstance(screen, Screen):
            raise TypeError("Expected a Screen instance.")

        self.screens[screen.name] = screen

    @abstractmethod
    def build(self) -> None:
        """Setup the application with initial screens."""
        pass

    def show_screen(self, screen_name: str) -> None:
        """Switch to a different screen by name."""
        if screen_name not in self.screens:
            print(f"Available screens: {list(self.screens.keys())}")
            raise ValueError(f"Screen '{screen_name}' not found.")

        if self.current_screen is not None:
            self.current_screen.unmount()

        self.current_screen = self.screens[screen_name]
        self.current_screen.mount(self.input_handler, self.renderer)

    def get_current_screen(self) -> Optional[Screen]:
        """Get the currently active screen."""
        return self.current_screen

    def get_screen(self, screen_name: str) -> Optional[Screen]:
        """Get a screen by name."""
        return self.screens.get(screen_name)

    def set_frame_rate(self, fps: int) -> None:
        """Set the target frame rate."""
        self._frame_rate = max(1, fps)
        self._frame_time = 1.0 / self._frame_rate

    async def _input_loop(self):
        """Run the input handler in an asynchronous loop."""
        while self._running:
            try:
                self.input_handler.process_input()
                await asyncio.sleep(0.001)
            except Exception as e:
                print(f"Input error: {e}")
                break

    async def _render_loop(self):
        """Run the renderer in an asynchronous loop."""
        while self._running:
            try:
                if not self.current_screen and self.screens:
                    first_screen_name = next(iter(self.screens.keys()))
                    self.show_screen(first_screen_name)

                if self.current_screen:
                    self.current_screen.refresh()

                self.renderer.render_frame()
                await asyncio.sleep(self._frame_time)
            except Exception as e:
                print(f"Render error: {e}")
                break

    async def _update_loop(self):
        """Run application updates at a slower rate."""
        while self._running:
            try:
                # Application-level updates can go here
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Update error: {e}")
                break

    async def run_async(self) -> None:
        """Run the application asynchronously."""
        try:
            self.build()
            self._register_decorated_keybinds()
            self._running = True

            await asyncio.gather(
                self._input_loop(),
                self._render_loop(),
                self._update_loop(),
                return_exceptions=True,
            )

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up application resources."""
        self._running = False

        if self.current_screen:
            self.current_screen.unmount()

        self.input_handler.stop()
        self.renderer.clear()

    def run(self) -> None:
        """Run the application synchronously."""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            pass
        finally:
            self._running = False

    def quit(self) -> None:
        """Quit the application gracefully."""
        self._running = False
        # Note: The actual cleanup will happen in the finally blocks of the loops

    def reload_screen(self, screen_name: Optional[str] = None) -> None:
        """Reload a screen (useful for development)."""
        target_screen = screen_name or (
            self.current_screen.screen_name if self.current_screen else None
        )

        if target_screen and target_screen in self.screens:
            was_current = (
                self.current_screen and self.current_screen.screen_name == target_screen
            )

            if was_current:
                if self.current_screen is not None:
                    self.current_screen.unmount()

            screen = self.screens[target_screen]
            screen.clear_children()
            screen.build()
            screen.layout_children()

            if was_current:
                screen.mount(self.input_handler, self.renderer)

    def get_all_screens(self) -> dict[str, Screen]:
        """Get all registered screens."""
        return self.screens.copy()

    def remove_screen(self, screen_name: str) -> None:
        """Remove a screen from the application."""
        if screen_name in self.screens:
            screen = self.screens[screen_name]

            if self.current_screen == screen:
                screen.unmount()
                self.current_screen = None

            del self.screens[screen_name]

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()
