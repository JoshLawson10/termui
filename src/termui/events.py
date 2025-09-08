from dataclasses import dataclass

from termui.dom import DOMNode
from termui.utils.geometry import Size
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


class Resize(Event):
    """Represents a resize event in the terminal.

    Args:
        size: The new size of the terminal.
    """

    size: Size


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

    x: int
    y: int
    """Coordinates of the mouse event."""
    button: int | None = None  # 0=left, 1=middle, 2=right, else None if a scroll event
    """The mouse button involved in the event."""
    widget: Widget | None = None
    """The widget under the mouse pointer."""

    def __repr__(self):
        return f"MouseEvent(x={self.x}, y={self.y}, button={self.button}, widget={self.widget})"


class MouseMove(MouseEvent):
    """Sent when the mouse is moved."""


class MouseDrag(MouseEvent):
    """Sent when the mouse is dragged."""


class MouseDown(MouseEvent):
    """Sent when a mouse button is pressed down."""


class MouseUp(MouseEvent):
    """Sent when a mouse button is released."""


class MouseScrollDown(MouseEvent):
    """Sent when the mouse is scrolled down."""


class MouseScrollUp(MouseEvent):
    """Sent when the mouse is scrolled up."""


class MouseScrollLeft(MouseEvent):
    """Sent when the mouse is scrolled left."""


class MouseScrollRight(MouseEvent):
    """Sent when the mouse is scrolled right."""


class Click(MouseEvent):
    """Sent when the mouse is clicked."""


class Enter(Event):
    """Sent when the mouse enters a widget.

    Args:
        node: The DOM node that was entered.
    """

    def __init__(self, node: DOMNode) -> None:
        super().__init__()
        self.node = node


class Leave(Event):
    """Sent when the mouse leaves a widget.

    Args:
        node: The DOM node that was left.
    """

    def __init__(self, node: DOMNode) -> None:
        super().__init__()
        self.node = node
