from typing import Optional

from termui.color import Color


class ColorTheme:
    def __init__(self, background_color: Optional[AnsiColor | RGBColor] = None) -> None:
        self.background_color = background_color
