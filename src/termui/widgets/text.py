from typing import Optional

from termui.colors.ansi import AnsiColor
from termui.colors.rgb import RGBColor
from termui.types.char import Char

from termui.widgets._widget import Widget


class Text(Widget):
    """A widget that displays text."""

    def __init__(
        self,
        content: str | list[str],
        **kwargs,
    ) -> None:
        super().__init__(name=kwargs.get("name", "Text"))
        self.content: list[str] = content if isinstance(content, list) else [content]
        self.fg_color = kwargs.get("fg_color", AnsiColor.WHITE)
        self.bg_color = kwargs.get("bg_color", None)
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
