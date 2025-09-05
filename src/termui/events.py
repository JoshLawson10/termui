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

    x: float
    y: float


@dataclass
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

    def __repr__(self):
        return f"KeyEvent(key={self.key})"


@dataclass
class MouseEvent(InputEvent):
    """Represents a mouse event with position and button information.

    Args:
        widget: The widget under the mouse pointer.
        x: The x-coordinate of the mouse event.
        y: The y-coordinate of the mouse event.
        button: The mouse button involved (0=left, 1=middle, 2=right).
    """

    widget: Widget | None
    """The widget under the mouse pointer."""
    x: float
    y: float
    """Coordinates of the mouse event."""
    button: int  # 0=left, 1=middle, 2=right
    """The mouse button involved in the event."""

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


@dataclass
class Enter(Event):
    """Sent when the mouse enters a widget.

    Args:
        node: The DOM node that was entered.
    """

    node: DOMNode


@dataclass
class Leave(Event):
    """Sent when the mouse leaves a widget.

    Args:
        node: The DOM node that was left.
    """

    node: DOMNode
