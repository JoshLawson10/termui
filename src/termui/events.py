from dataclasses import dataclass
from typing import Optional

from termui.widgets._widget import Widget


@dataclass
class MouseEvent:
    """Represents a mouse event with position and button information."""

    x: int
    y: int
    button: int  # 0=left, 1=middle, 2=right
    event_type: str  # 'press', 'release', 'move', 'drag'
    widget: Optional[Widget] = None

    def __repr__(self):
        return f"MouseEvent(x={self.x}, y={self.y}, button={self.button}, type={self.event_type})"
