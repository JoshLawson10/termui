import uuid
from abc import ABC, abstractmethod
from typing import Optional

from termui.char import Char
from termui.dom import DOMNode
from termui.events import MouseEvent
from termui.utils.geometry import Region


class Widget(DOMNode, ABC):
    """Base class for all widgets in the TermUI framework.

    Widgets are visual components that can be rendered to the terminal.
    They inherit from DOMNode to participate in the DOM tree structure
    and must implement the render() method to define their appearance.
    """

    def __init__(self, name: Optional[str] = None, **kwargs) -> None:
        """Initialize the widget with position, size, and identification.

        Args:
            name: Optional display name for the widget. If not provided,
                 generates a name using the class name and part of the ID.
            **kwargs: Additional widget properties:
                id: Unique identifier (auto-generated if not provided).
                x, y: Position coordinates (default: 0, 0).
                width, height: Dimensions (default: 0, 0).
                pos: Grid position for layout widgets (default: (0, 0)).
        """
        self.id = kwargs.get("id", str(uuid.uuid4()))
        """Unique identifier for the widget."""
        self.name = name or f"Widget_{self.id[:8]}"
        """Name of the widget. Acts as its class name when used in the DOM with 'get_widget_by_name'"""
        super().__init__(id=self.id, name=self.name, widget=self)

        self.region = Region(
            kwargs.get("x", 0),
            kwargs.get("y", 0),
            kwargs.get("width", 0),
            kwargs.get("height", 0),
        )
        """The region occupied by the widget."""

        self.pos: tuple[int | tuple[int, int], int | tuple[int, int]] = kwargs.get(
            "pos", (0, 0)
        )
        """Grid position of the widget in the layout grid."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}): Pos({self.pos})"

    def __call__(self, *children: "Widget") -> "Widget":
        """Make the widget callable to accept children.

        This allows syntax like:
        ```python
        container = Container(title="My Container")

        return container(
            Text("Child 1"),
            Text("Child 2")
        )
        ```

        Args:
            *children: Child widgets to add to this widget.

        Returns:
            Self, to allow method chaining and use in layouts.
        """
        self.add_children(*children)
        return self

    def set_position(self, x: int, y: int) -> None:
        """Set the widget's position.

        Args:
            x: The x-coordinate to position the widget at.
            y: The y-coordinate to position the widget at.
        """
        self.region.move_absolute(x, y)

    def set_size(self, width: int, height: int) -> None:
        """Set the widget's size.

        Args:
            width: The width to set for the widget.
            height: The height to set for the widget.
        """
        self.region.update_dimensions(width, height)

    def get_minimum_size(self) -> tuple[int, int]:
        """Get the minimum size required for this widget.

        Returns:
            A tuple (width, height) representing the minimum space needed
            to properly display this widget. Default implementation returns
            (0, 0), but widgets should override this to provide meaningful
            size constraints.
        """
        return 0, 0

    def handle_mouse_event(self, event: MouseEvent) -> None:
        """Handle a mouse event that occurred within this widget.

        Args:
            event: The mouse event to handle. Routes to specific handler
                  methods based on the event type.
        """
        if event.event_type == "press":
            self._on_click(event)
        else:
            self._on_mouse_enter()

    def _on_mouse_enter(self) -> None:
        """Handle mouse enter events.

        Called when the mouse cursor enters the widget's region.
        Override in subclasses to implement hover effects.
        """
        pass

    def _on_mouse_exit(self) -> None:
        """Handle mouse exit events.

        Called when the mouse cursor leaves the widget's region.
        Override in subclasses to clean up hover effects.
        """
        pass

    def _on_click(self, event: MouseEvent) -> None:
        """Handle mouse click events.

        Override in subclasses to implement click behavior.

        Args:
            event: The mouse click event with position and button information.
        """
        pass

    @abstractmethod
    def render(self) -> list[list[Char]]:
        """Render the widget to a 2D array of characters.

        Returns:
            A 2D list of Char objects representing the widget's visual
            appearance. The dimensions should match the widget's region
            size (width x height).
        """
        pass
