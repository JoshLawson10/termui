from .screen import Screen
from abc import ABC, abstractmethod


class App(ABC):
    def __init__(self) -> None:
        self.screens: dict[str, Screen] = {}
        self.current_screen: Screen | None = None

    def register_screen(self, screen: Screen) -> None:
        """Register a new screen."""
        if not isinstance(screen, Screen):
            raise TypeError("Expected a Screen instance.")
        screen.setup()
        self.screens[screen.name] = screen
        print(f"Registered screen: {screen.name}")

    @abstractmethod
    def setup(self) -> None:
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
            self.current_screen = self.screens[screen_name]
        else:
            raise ValueError(f"Screen '{screen_name}' not found.")

    def get_current_screen(self) -> Screen | None:
        """Get the currently active screen."""
        return self.current_screen

    def run(self) -> None:
        """Run the application."""
        self.setup()
        self.update()
        if self.current_screen is None:
            raise RuntimeError("No current screen set.")
        self.current_screen.render()
