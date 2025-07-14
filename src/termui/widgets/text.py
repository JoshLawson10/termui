from typing import Optional

from termui.widgets._widget import Widget
from termui.types.char import Char
from termui.colors.ansi import AnsiColor
from termui.colors.rgb import RGBColor


class Text(Widget):
    """A widget that displays text."""

    def __init__(
        self,
        content: str | list[str],
        fg_color: Optional[AnsiColor | RGBColor] = None,
        bg_color: Optional[AnsiColor | RGBColor] = None,
    ) -> None:
        super().__init__(name="Text")
        self.content: list[str] = content if isinstance(content, list) else [content]
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.update_dimensions(
            width=max(len(line) for line in self.content), height=len(self.content)
        )

    def render(self) -> list[list[Char]]:
        rendered_content: list[list[Char]] = []
        for line in self.content:
            rendered_line: list[Char] = []
            for char in line:
                rendered_char: Char = Char(char, self.fg_color, self.bg_color)
                rendered_line.append(rendered_char)
            rendered_content.append(rendered_line)
        return rendered_content
