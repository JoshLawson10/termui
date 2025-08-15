from dataclasses import dataclass
from typing import Optional

from termui.color import Color


@dataclass
class Char:
    """Represents a character with optional foreground and background colors."""

    char: str
    fg_color: Optional[Color] = None
    bg_color: Optional[Color] = None
