from abc import ABC, abstractmethod


class Widget(ABC):
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.width = 0
        self.height = 0

    def update_dimensions(self, width: int, height: int) -> None:
        """Update the dimensions of the widget."""
        self.width = width
        self.height = height

    @abstractmethod
    def render(self) -> list[list[str]]:
        """Render the widget."""
        pass
