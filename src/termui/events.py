from dataclasses import dataclass
from typing import TYPE_CHECKING

from termui.utils.geometry import Size

if TYPE_CHECKING:
    from termui.dom_tree import DOMNode
    from termui.widget import Widget


class Event:
    """Base class for all events."""


@dataclass
class CursorPosition(Event):
    """Represents the position of the cursor in the terminal.

    Args:
        x: The x-coordinate of the cursor.
        y: The y-coordinate of the cursor.
    """

    x: int
    y: int


@dataclass
class Resize(Event):
    """Represents a resize event in the terminal.

    Args:
        size: The new size of the terminal.
    """

    size: Size
    pixel_size: Size | None = None

    @classmethod
    def from_dimensions(
        cls, cells: tuple[int, int], pixels: tuple[int, int] | None = None
    ) -> "Resize":
        """Construct from basic dimensions.

        Args:
            cells: tuple of (width, height) in cells.
            pixels: tuple of (width, height) in pixels if known, or `None` if not known.

        """
        size = Size(*cells)
        pixel_size = Size(*pixels) if pixels is not None else None
        return Resize(size, pixel_size)


class Mount(Event):
    """Sent when a widget or screen is mounted."""


class Unmount(Event):
    """Sent when a widget or screen is unmounted."""


class InputEvent(Event):
    """Base class for all input events."""


@dataclass
class Key(InputEvent):
    """Represents a keyboard event with key information.

    Args:
        key: The key that was pressed, as a string identifier.
    """

    key: str
    """The key that was pressed, as a string identifier."""
    character: str | None = None
    """The character representation of the key, if applicable."""

    def __repr__(self):
        return f"KeyEvent(key={self.key}, char={self.character})"


@dataclass
class MouseEvent(InputEvent):
    """Represents a mouse event with position and button information.

    Args:
        x: The x-coordinate of the mouse event.
        y: The y-coordinate of the mouse event.
        button: The mouse button involved (0=left, 1=middle, 2=right).
        widget: The widget under the mouse pointer.
    """

    x: float
    y: float
    """Coordinates of the mouse event."""
    button: int | None = None  # 0=left, 1=middle, 2=right, else None if a scroll event
    """The mouse button involved in the event."""
    widget: "Widget | None" = None
    """The widget under the mouse pointer."""

    def __repr__(self):
        return f"MouseEvent(x={self.x}, y={self.y}, button={self.button}, widget={self.widget})"


class MouseMove(MouseEvent):
    """Sent when the mouse is moved."""

    def __repr__(self):
        return f"MouseMove(x={self.x}, y={self.y}, widget={self.widget})"


class MouseDrag(MouseEvent):
    """Sent when the mouse is dragged."""

    def __repr__(self):
        return f"MouseDrag(x={self.x}, y={self.y}, button={self.button}, widget={self.widget})"


class MouseDown(MouseEvent):
    """Sent when a mouse button is pressed down."""

    def __repr__(self):
        return f"MouseDown(x={self.x}, y={self.y}, button={self.button}, widget={self.widget})"


class MouseUp(MouseEvent):
    """Sent when a mouse button is released."""

    def __repr__(self):
        return f"MouseUp(x={self.x}, y={self.y}, button={self.button}, widget={self.widget})"


@dataclass
class MouseScrollEvent(MouseEvent):
    """Base class for events when the mouse is scrolled."""

    dx: float = 0.0
    dy: float = 0.0


class MouseScrollDown(MouseScrollEvent):
    """Sent when the mouse is scrolled down."""

    def __repr__(self):
        return f"MouseScrollDown(x={self.x}, y={self.y}, dx={self.dx}, dy={self.dy}, button={self.button}, widget={self.widget})"


class MouseScrollUp(MouseScrollEvent):
    """Sent when the mouse is scrolled up."""

    def __repr__(self):
        return f"MouseScrollUp(x={self.x}, y={self.y}, dx={self.dx}, dy={self.dy}, button={self.button}, widget={self.widget})"


class MouseScrollLeft(MouseScrollEvent):
    """Sent when the mouse is scrolled left."""

    def __repr__(self):
        return f"MouseScrollLeft(x={self.x}, y={self.y}, dx={self.dx}, dy={self.dy}, button={self.button}, widget={self.widget})"


class MouseScrollRight(MouseScrollEvent):
    """Sent when the mouse is scrolled right."""

    def __repr__(self):
        return f"MouseScrollRight(x={self.x}, y={self.y}, dx={self.dx}, dy={self.dy}, button={self.button}, widget={self.widget})"


@dataclass
class Enter(Event):
    """Sent when the mouse enters a widget.

    Args:
        node: The DOM node that was entered.
    """

    node: "DOMNode"


@dataclass
class Leave(Event):
    """Sent when the mouse leaves a widget.

    Args:
        node: The DOM node that was left.
    """

    node: "DOMNode"
