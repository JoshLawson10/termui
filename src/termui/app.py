from .screen import Screen
from .input import InputHandler, Keybind
from abc import ABC, abstractmethod
import inspect


class App(ABC):
    def __init__(self) -> None:
        self.screens: dict[str, Screen] = {}
        self.current_screen: Screen | None = None
        self.input_handler = InputHandler()

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
        screen.build()
        self.screens[screen.name] = screen

    @abstractmethod
    def build(self) -> None:
        """Setup the application with initial screens.

        This method is intended to be overridden by the inheriting class."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the application state.

        This method is intended to be overridden by the inheriting class."""
        pass

    def show_screen(self, screen_name: str) -> None:
        """Switch to a different screen by name."""
        if screen_name in self.screens:
            if self.current_screen is not None:
                self.current_screen.unmount()
            self.current_screen = self.screens[screen_name]
            self.current_screen.mount(self.input_handler)
        else:
            raise ValueError(f"Screen '{screen_name}' not found.")

    def get_current_screen(self) -> Screen | None:
        """Get the currently active screen."""
        return self.current_screen

    def run(self) -> None:
        """Run the application."""
        self.build()
        self._register_decorated_keybinds()

        try:
            while True:
                self.input_handler.process_input()
                self.update()
        except KeyboardInterrupt:
            pass
