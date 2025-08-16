from termui.char import Char
from termui.color import Color
from termui.layout import Layout
from termui.layouts import VerticalLayout
from termui.utils.align import HorizontalAlignment, VerticalAlignment
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from termui.utils.geometry import Region
from termui.widget import Widget


class Container(Widget):
    """A container widget that can hold and organize child widgets."""

    def __init__(self, *children, **kwargs) -> None:
        """Initialize a container with optional child widgets.

        Args:
            *children: Child widgets to add to the container.
            border_style: Style of the border, by default "solid".
            border_color: Color of the border, by default white.
            padding: Padding (top, right, bottom, left), by default (0, 0, 0, 0).
            title: Title to display on the border, by default None.
            title_color: Color of the title text, by default white.
            title_alignment: Alignment of the title, by default "left".
            layout: Custom layout for arranging children, by default VerticalLayout.
            **kwargs: Additional widget parameters.
        """
        super().__init__(
            name=kwargs.get("name", f"Container-{kwargs.get('title', None)}"), **kwargs
        )

        self.title = kwargs.get("title", None)
        """The title displayed at the top of the container."""
        self.title_color = kwargs.get("title_color", Color(255, 255, 255))
        """The color of the title text."""
        self.title_alignment: HorizontalAlignment = kwargs.get(
            "title_alignment", "left"
        )
        """The alignment of the title text."""
        self.border_style: BorderStyle = kwargs.get("border_style", "solid")
        """The style of the container's border."""
        self.border_color = kwargs.get("border_color", Color(255, 255, 255))
        """The color of the container's border."""
        self.padding = kwargs.get("padding", (0, 0, 0, 0))
        """The padding inside the container."""

        self.children: list[Widget] = []
        """A list of child widgets contained within this container."""
        self._content_layout: Layout = kwargs.get("layout", VerticalLayout)
        """The layout direction for the container's content."""

        for child in children:
            self.add_child(child)

        min_width, min_height = self.get_minimum_size()
        self.set_size(kwargs.get("width", min_width), kwargs.get("height", min_height))

    def add_child(self, child: Widget) -> None:
        """Add a child widget to the container.

        Overrides Widget.add_child to locally manage children within the container.

        Args:
            child (Widget): The child widget to add.
        """
        if child not in self.children:
            self.children.append(child)
            super().add_child(child)
            if child not in self._content_layout.children:
                self._content_layout.children.append(child)
            self._arrange_content()
            self.mark_dirty()

    def remove_child(self, child: Widget) -> None:
        """Remove a child widget from the container.

        Overrides Widget.remove_child to locally manage children within the container.

        Args:
            child (Widget): The child widget to remove.
        """
        if child in self.children:
            self.children.remove(child)
            super().remove_child(child)
            if child in self._content_layout.children:
                self._content_layout.children.remove(child)
            self._arrange_content()
            self.mark_dirty()

    def clear_children(self) -> None:
        """Remove all child widgets from the container."""
        for child in self.children.copy():
            self.remove_child(child)

    def get_content_region(self) -> Region:
        """Get the region available for content (inside border and padding)."""
        border_offset = 1 if self.border_style != "none" else 0

        content_x = border_offset + self.padding[3]
        content_y = border_offset + self.padding[0]
        content_width = (
            self.region.width - (border_offset * 2) - self.padding[1] - self.padding[3]
        )
        content_height = (
            self.region.height - (border_offset * 2) - self.padding[0] - self.padding[2]
        )

        return Region(
            self.region.x + content_x,
            self.region.y + content_y,
            max(0, content_width),
            max(0, content_height),
        )

    def _arrange_content(self) -> None:
        """Arrange the content layout within the container."""
        if not self.children:
            return

        content_region = self.get_content_region()

        self._content_layout.set_position(content_region.x, content_region.y)
        self._content_layout.set_size(content_region.width, content_region.height)

        self._content_layout.arrange()

    def set_size(self, width: int, height: int) -> None:
        """Set the size of the container and rearrange content.

        Args:
            width (int): The new width of the container.
            height (int): The new height of the container.
        """
        super().set_size(width, height)
        self._arrange_content()

    def set_position(self, x: int, y: int) -> None:
        """Set the position of the container and rearrange content.

        Args:
            x (int): The new x-coordinate of the container.
            y (int): The new y-coordinate of the container.
        """
        super().set_position(x, y)
        self._arrange_content()

    def get_minimum_size(self) -> tuple[int, int]:
        """Calculate the minimum size needed to display the container and its contents.

        Returns:
            A tuple (min_width, min_height) representing the minimum space
            required for the container including padding and borders.
        """
        border_size = 2 if self.border_style != "none" else 0

        padding_width = self.padding[1] + self.padding[3]
        padding_height = self.padding[0] + self.padding[2]

        content_min_width, content_min_height = 0, 0
        if self.children:
            if hasattr(self._content_layout, "calculate_minimum_size"):
                content_min_width, content_min_height = (
                    self._content_layout.calculate_minimum_size()
                )
            else:
                content_min_width = max(child.region.width for child in self.children)
                content_min_height = sum(child.region.height for child in self.children)

        min_width = border_size + padding_width + content_min_width
        min_height = border_size + padding_height + content_min_height

        if self.border_style != "none" or self.title:
            min_width = max(min_width, 3)
            min_height = max(min_height, 3)

        return max(min_width, 1), max(min_height, 1)

    def render(self) -> list[list[Char]]:
        """Render the container with its border and children."""
        content = draw_rectangle(
            self.region.width,
            self.region.height,
            border_style=self.border_style,
            border_color=self.border_color,
            title=self.title,
            title_color=self.title_color,
            title_alignment=self.title_alignment,
        )

        if self.children:
            for child in self.children:
                if child.region.width > 0 and child.region.height > 0:
                    child_content = child.render()

                    rel_x = child.region.x - self.region.x
                    rel_y = child.region.y - self.region.y

                    for row_idx, row in enumerate(child_content):
                        y_pos = rel_y + row_idx
                        if 0 <= y_pos < len(content):
                            for col_idx, char in enumerate(row):
                                x_pos = rel_x + col_idx
                                if 0 <= x_pos < len(content[y_pos]):
                                    content[y_pos][x_pos] = char

        return content

    def update_title(self, title: str) -> None:
        """Update the title of the container.

        Args:
            title (str): The new title for the container.
        """
        self.title = title
        self.mark_dirty()

    def set_border_style(self, style: BorderStyle) -> None:
        """Update the border style of the container.

        Args:
            style (BorderStyle): The new border style for the container.
        """
        self.border_style = style
        self.mark_dirty()

    def set_border_color(self, color: Color) -> None:
        """Update the border color of the container.

        Args:
            color (Color): The new border color for the container.
        """
        self.border_color = color
        self.mark_dirty()

    def set_padding(self, padding: tuple[int, int, int, int]) -> None:
        """Update the padding of the container.

        Args:
            padding (tuple[int, int, int, int]): The new padding values (top, right, bottom, left).
        """
        self.padding = padding
        self._arrange_content()
        self.mark_dirty()
