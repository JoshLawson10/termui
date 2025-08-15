from dataclasses import dataclass


class InputEvent:
    """Base class for all input events."""


@dataclass
class MouseEvent(InputEvent):
    """Represents a mouse event with position and button information.

    Args:
        x: The x-coordinate of the mouse event.
        y: The y-coordinate of the mouse event.
        button: The mouse button involved (0=left, 1=middle, 2=right).
        event_type: The type of mouse event ('press', 'release', 'move', 'drag').
    """

    x: int
    y: int
    """Coordinates of the mouse event."""
    button: int  # 0=left, 1=middle, 2=right
    """The mouse button involved in the event."""
    event_type: str  # 'press', 'release', 'move', 'drag'
    """The type of mouse event."""

    def __repr__(self):
        return f"MouseEvent(x={self.x}, y={self.y}, button={self.button}, type={self.event_type})"


@dataclass
class KeyEvent(InputEvent):
    """Represents a keyboard event with key information.

    Args:
        key: The key that was pressed, as a string identifier.
    """

    key: str
    """The key that was pressed, as a string identifier."""

    def __repr__(self):
        return f"KeyEvent(key={self.key})"
