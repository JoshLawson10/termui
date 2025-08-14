from dataclasses import dataclass


class InputEvent:
    """Represents a generic input event."""


@dataclass
class MouseEvent(InputEvent):
    """Represents a mouse event with position and button information."""

    x: int
    y: int
    button: int  # 0=left, 1=middle, 2=right
    event_type: str  # 'press', 'release', 'move', 'drag'

    def __repr__(self):
        return f"MouseEvent(x={self.x}, y={self.y}, button={self.button}, type={self.event_type})"


@dataclass
class KeyEvent(InputEvent):
    """Represents a keyboard event with key information."""

    key: str

    def __repr__(self):
        return f"KeyEvent(key={self.key})"
