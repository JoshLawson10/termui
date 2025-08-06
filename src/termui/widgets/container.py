from termui.colors import AnsiColor, RGBColor
from termui.types.char import Char
from termui.utils.align import HorizontalAlignment, VerticalAlignment
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from ._widget import Widget


class Container(Widget):
    def __init__(self, *children, **kwargs) -> None:
        super().__init__(name=kwargs.get("name", "Container"))
        min_width = max(len(child) for child in children) if children else 0
        min_height = len(children) if children else 0
        self.set_size(kwargs.get("width", min_width), kwargs.get("height", min_height))
        self.border_style: BorderStyle = kwargs.get("border_style", "solid")
        self.border_color = kwargs.get("border_color", AnsiColor.WHITE)
        self.padding = kwargs.get("padding", (0, 0, 0, 0))
        self.title = kwargs.get("title", None)
        self.title_color = kwargs.get("title_color", AnsiColor.WHITE)
        self.title_alignment: HorizontalAlignment = kwargs.get(
            "title_alignment", "left"
        )

    def render(self) -> list[list[Char]]:
        content = draw_rectangle(
            self.region.width,
            self.region.height,
            border_style=self.border_style,
            border_color=self.border_color,
            title=self.title,
            title_color=self.title_color,
            title_alignment=self.title_alignment,
        )
        return content

    def update_title(self, title: str) -> None:
        """Update the title of the container."""
        self.title = title
