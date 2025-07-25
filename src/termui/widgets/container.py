from typing import List

from termui.types.char import Char
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from termui.utils.align import HorizontalAlignment
from termui.widgets._base_container import BaseContainerWidget
from termui.colors import AnsiColor


class Container(BaseContainerWidget):
    """A container widget that can hold other widgets with optional border."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("width", kwargs.get("width", 20))
        kwargs.setdefault("height", kwargs.get("height", 10))

        super().__init__(**kwargs)

        self.border_style: BorderStyle = kwargs.get("border_style", "solid")
        self.border_color = kwargs.get("border_color", AnsiColor.WHITE)
        self.background_color = kwargs.get("background_color", None)
        self.padding = kwargs.get("padding", (1, 1, 1, 1))  # top, right, bottom, left
        self.title = kwargs.get("title", None)
        self.title_color = kwargs.get("title_color", AnsiColor.WHITE)
        self.title_alignment: HorizontalAlignment = kwargs.get(
            "title_alignment", "left"
        )

    def set_title(self, title: str) -> None:
        """Set the container title."""
        if title != self.title:
            self.title = title
            self.mark_dirty()

    def update_title(self, title: str) -> None:
        """Update the container title (legacy compatibility)."""
        self.set_title(title)

    def set_border_style(self, style: BorderStyle) -> None:
        """Set the border style."""
        if style != self.border_style:
            self.border_style = style
            self.mark_dirty()

    def get_content_area(self) -> tuple[int, int, int, int]:
        """Get the content area (x, y, width, height) inside the container."""
        if self.border_style == "none":
            border_width = 0
        else:
            border_width = 1

        padding_top, padding_right, padding_bottom, padding_left = self.padding

        content_x = border_width + padding_left
        content_y = border_width + padding_top
        content_width = max(
            0, self.width - 2 * border_width - padding_left - padding_right
        )
        content_height = max(
            0, self.height - 2 * border_width - padding_top - padding_bottom
        )

        return content_x, content_y, content_width, content_height

    def layout_children(self) -> None:
        """Layout children within the content area."""
        if self.layout_manager and self.children:
            content_x, content_y, content_width, content_height = (
                self.get_content_area()
            )

            original_width, original_height = self.width, self.height
            self.width, self.height = content_width, content_height
            self.layout_manager.layout(self, self.children)

            for child in self.children:
                child.set_position(child.x + content_x, child.y + content_y)

            self.width, self.height = original_width, original_height

            self.mark_dirty()

    def render(self) -> List[List[Char]]:
        """Render the container with border and background."""
        if self.border_style == "none":
            fill_char = Char(" ", None, self.background_color)
            content = [
                [fill_char for _ in range(self.width)] for _ in range(self.height)
            ]
        else:
            fill_char = Char(" ", None, self.background_color)
            content = draw_rectangle(
                self.width,
                self.height,
                border_style=self.border_style,
                border_color=self.border_color,
                title=self.title,
                title_color=self.title_color,
                title_alignment=self.title_alignment,
                fill=fill_char,
            )

        return content
