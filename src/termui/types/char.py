from dataclasses import dataclass
from typing import Optional

from termui.colors.ansi import AnsiColor
from termui.colors.rgb import RGBColor


@dataclass
class Char:
    char: str
    fg_color: Optional[AnsiColor | RGBColor] = None
    bg_color: Optional[AnsiColor | RGBColor] = None
