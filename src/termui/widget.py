import uuid
from abc import ABC, abstractmethod

from termui import events
from termui.char import Char
from termui.dom_node import DOMNode
from termui.logger import log
from termui.utils.geometry import Region


class Widget(DOMNode, ABC):
    """Base class for all widgets in the TermUI framework.

    Widgets are visual components that can be rendered to the terminal.
    They inherit from DOMNode to participate in the DOM tree structure
    and must implement the render() method to define their appearance.
    """

    def __init__(self, **kwargs) -> None:
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
        self.name = kwargs.get("name", f"{self.__class__.__name__}-{self.id[:8]}")
        """Name of the widget. Acts as its class name when used in the DOM with 'get_widget_by_name'"""
        super().__init__(id=self.id, name=self.name)

        self.region = Region(
            kwargs.get("x", 0),
            kwargs.get("y", 0),
            kwargs.get("width", 0),
            kwargs.get("height", 0),
        )
        """The region occupied by the widget."""

        self.grid_pos: tuple[int | tuple[int, int], int | tuple[int, int]] = kwargs.get(
            "pos", (0, 0)
        )
        """Grid position of the widget in the layout grid."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}): Grid Pos({self.grid_pos})"

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

    def handle_mouse_event(self, event: events.MouseEvent) -> None:
        """Handle a mouse event that occurred within this widget.

        Args:
            event: The mouse event to handle. Routes to specific handler
                  methods based on the event type.
        """
        if self.region.contains(int(event.x), int(event.y)):
            if isinstance(event, events.MouseDown):
                self._on_mouse_down(event)
            elif isinstance(event, events.MouseUp):
                self._on_mouse_up(event)
            elif isinstance(event, events.MouseScrollEvent):
                self._on_mouse_scroll(event)
            elif isinstance(event, events.Enter):
                self._on_mouse_enter()
                log.system(f"Mouse entered at ({event.x}, {event.y})")
        else:
            self._on_mouse_exit()

    def _on_mouse_enter(self) -> None:
        """Handle mouse enter events.

        Called when the mouse cursor enters the widget's region.
        Override in subclasses to implement hover effects.
        """

    def _on_mouse_exit(self) -> None:
        """Handle mouse exit events.

        Called when the mouse cursor leaves the widget's region.
        Override in subclasses to clean up hover effects.
        """

    def _on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse down events.

        Override in subclasses to implement press behavior.

        Args:
            event: The mouse event to handle. Routes to specific handler
        """

    def _on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle mouse up events.

        Override in subclasses to implement release behavior.

        Args:
            event: The mouse event to handle. Routes to specific handler
        """

    def _on_mouse_scroll(self, event: events.MouseScrollEvent) -> None:
        """Handle mouse scroll events.

        Override in subclasses to implement scroll behavior.

        Args:
            event: The mouse event to handle. Routes to specific handler
        """

    @abstractmethod
    def render(self) -> list[list[Char]]:
        """Render the widget to a 2D array of characters.

        Returns:
            A 2D list of Char objects representing the widget's visual
            appearance. The dimensions should match the widget's region
            size (width x height).
        """
        raise NotImplementedError("Subclasses must implement the render method.")
