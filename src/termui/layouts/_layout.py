from abc import abstractmethod
from typing import Optional

from termui.widgets._widget import Widget


class Layout(Widget):
    """An abstract base class for layouts."""

    def __init__(self, name: Optional[str] = None, *children: Widget) -> None:
        super().__init__(name=name or "Layout")
        self.children: list[Widget] = list(children)
        self.arrange()

    @abstractmethod
    def arrange(self) -> None:
        """Arrange the widgets on the screen.

        This method should be implemented by subclasses to define how widgets are placed.
        """
        raise NotImplementedError("Subclasses must implement the arrange method.")

    def render(self) -> list[list[str]]:
        """Placeholder needed for compatibility with Widget's render method."""
        self.arrange()
        return [[]]
