from abc import abstractmethod
from typing import Optional

from termui.widget import Widget


class Layout(Widget):
    """Abstract base class for all layout widgets.

    Layouts are special widgets that arrange and position child widgets
    according to specific rules. They handle automatic sizing, positioning,
    and spacing of their children.
    """

    def __init__(self, *, name: Optional[str] = None, **kwargs) -> None:
        """Initialize the layout with child widgets.

        Args:
            name: Optional name for the layout. Defaults to "Layout".
            *children: Variable number of child widgets to include in the layout.
            **kwargs: Additional keyword arguments, including:
                spacing: Space between child widgets (default: 0).
        """
        super().__init__(name=name or "Layout")
        self.children: list[Widget] = []
        """A list of child widgets contained in the layout."""
        self.spacing = kwargs.get("spacing", 0)
        """The space between child widgets."""

    def __call__(self, *children: Widget) -> "Layout":
        """Make the layout callable to accept child widgets.

        Args:
            *children: Variable number of child widgets to include in the layout.
        """
        self.children.extend(children)
        return self

    @abstractmethod
    def arrange(self) -> None:
        """Arrange the child widgets according to the layout's rules.

        This method must be implemented by subclasses to define how widgets
        are positioned and sized within the layout. It should set the position
        and size of all child widgets based on the layout's algorithm.
        """
        raise NotImplementedError("Subclasses must implement the arrange method.")

    def calculate_minimum_size(self) -> tuple[int, int]:
        """Calculate the minimum size required for the layout.

        Returns:
            A tuple (min_width, min_height) representing the minimum space
            required for the layout including padding and borders.
        """
        raise NotImplementedError(
            "Subclasses must implement the calculate_minimum_size method."
        )

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

    def add_child(self, child: Widget) -> None:
        """Add a child widget to the layout.

        Args:
            child: The child widget to add.
        """
        self.children.append(child)
        self.arrange()
