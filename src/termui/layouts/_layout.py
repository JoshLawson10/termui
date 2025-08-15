from abc import abstractmethod
from typing import Optional

from termui.widgets._widget import Widget


class Layout(Widget):
    """Abstract base class for all layout widgets.

    Layouts are special widgets that arrange and position child widgets
    according to specific rules. They handle automatic sizing, positioning,
    and spacing of their children.
    """

    def __init__(self, name: Optional[str] = None, *children: Widget, **kwargs) -> None:
        """Initialize the layout with child widgets.

        Args:
            name: Optional name for the layout. Defaults to "Layout".
            *children: Variable number of child widgets to include in the layout.
            **kwargs: Additional keyword arguments, including:
                spacing: Space between child widgets (default: 0).
        """
        super().__init__(name=name or "Layout")
        self.children: list[Widget] = list(children)
        """A list of child widgets contained in the layout."""
        self.spacing = kwargs.get("spacing", 0)
        """The space between child widgets."""

        self.arrange()

    @abstractmethod
    def arrange(self) -> None:
        """Arrange the child widgets according to the layout's rules.

        This method must be implemented by subclasses to define how widgets
        are positioned and sized within the layout. It should set the position
        and size of all child widgets based on the layout's algorithm.
        """
        raise NotImplementedError("Subclasses must implement the arrange method.")

    def render(self) -> list[list[str]]:
        """Render the layout by arranging its children.

        This is a placeholder implementation that calls arrange() to ensure
        child widgets are properly positioned before rendering.

        Returns:
            An empty 2D list as layouts typically don't render content themselves,
            only arrange their children.
        """
        self.arrange()
        return [[]]
