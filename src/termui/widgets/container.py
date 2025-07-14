from typing import Optional


from ._widget import Widget
from termui.colors import AnsiColor, RGBColor
from termui.types.char import Char
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from termui.utils.align import HorizontalAlignment


class Container(Widget):
    def __init__(
        self,
        width: int,
        height: int,
        title: Optional[str] = None,
        *,
        name: str = "Container",
        border_style: BorderStyle = "solid",
        border_color: AnsiColor | RGBColor = AnsiColor.WHITE,
        title_color: AnsiColor | RGBColor = AnsiColor.WHITE,
        title_alignment: HorizontalAlignment = "left",
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
    ) -> None:
        super().__init__(name=name)
        self.update_dimensions(width, height)
        self.border_style: BorderStyle = border_style
        self.border_color = border_color
        self.padding = padding
        self.title = title
        self.title_color = title_color
        self.title_alignment: HorizontalAlignment = title_alignment

    def render(self) -> list[list[Char]]:
        content = draw_rectangle(
            self.width,
            self.height,
            border_style=self.border_style,
            border_color=self.border_color,
            title=self.title,
            title_color=self.title_color,
            title_alignment=self.title_alignment,
        )
        return content
