from dataclasses import dataclass
from typing import Optional

from termui.color import Color


@dataclass
class Char:
    char: str
    fg_color: Optional[Color] = None
    bg_color: Optional[Color] = None
