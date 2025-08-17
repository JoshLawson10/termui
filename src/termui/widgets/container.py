from typing import Optional

from termui.char import Char
from termui.color import Color
from termui.layout import Layout
from termui.layouts import VerticalLayout
from termui.utils.align import HorizontalAlignment
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from termui.utils.geometry import Region
from termui.widget import Widget


class Container(Widget):
    """A container widget that can hold and organize child widgets."""

    def __init__(self, root_layout: Optional[Layout] = None, **kwargs) -> None:
        """Initialize a container with optional child widgets.

        Args:
            root_layout (Layout): The root layout to manage child widgets.
                All widgets to be contained in this should be added to this layout.
                If None, creates a VerticalLayout by default.
            border_style: Style of the border, by default "solid".
            border_color: Color of the border, by default white.
            padding: Padding (top, right, bottom, left), by default (0, 0, 0, 0).
            title: Title to display on the border, by default None.
            title_color: Color of the title text, by default white.
            title_alignment: Alignment of the title, by default "left".
            **kwargs: Additional widget parameters.
        """
        super().__init__(
            name=kwargs.get("name", f"Container-{kwargs.get('title', 'Unnamed')}"),
            **kwargs,
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

        self.root_layout = root_layout if root_layout else VerticalLayout()
        """The root layout to manage child widgets."""

        self._sizing_in_progress = False
        """Flag to prevent infinite sizing loops."""

        self.add_child(self.root_layout)

    def __call__(self, *children: Widget) -> "Container":
        """Make the container callable to accept children.

        This allows syntax like:
        container = Container(title="My Container")(
            Text("Child 1"),
            Text("Child 2")
        )

        Args:
            *children: Child widgets to add to this container.

        Returns:
            Self, to allow method chaining and use in layouts.
        """

        for child in children:
            self.root_layout.add_child(child)

        return self

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
        if not self.root_layout:
            return

        content_region = self.get_content_region()

        if content_region.width > 0 and content_region.height > 0:
            self.root_layout.set_position(content_region.x, content_region.y)
            self.root_layout.set_size(content_region.width, content_region.height)
            self.root_layout.arrange()

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

        min_width = border_size + padding_width + 10
        min_height = border_size + padding_height + 3

        return min_width, min_height

    def render(self) -> list[list[Char]]:
        """Render the container with its border and children."""
        self._arrange_content()

        content = draw_rectangle(
            self.region.width,
            self.region.height,
            border_style=self.border_style,
            border_color=self.border_color,
            title=self.title,
            title_color=self.title_color,
            title_alignment=self.title_alignment,
        )

        if self.root_layout and self.root_layout.children:
            for child_node in self.root_layout.children:
                child = (
                    child_node.widget if hasattr(child_node, "widget") else child_node
                )

                if child and child.region.width > 0 and child.region.height > 0:
                    try:
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
                    except Exception as e:
                        pass

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

    def set_layout(self, layout: Layout) -> None:
        """Replace the current layout with a new one.

        Args:
            layout: The new layout to use for arranging children.
        """
        if self.root_layout and self.root_layout.children:
            old_children = list(self.root_layout.children)
            self.root_layout.children.clear()

            for child in old_children:
                layout.add_child(child)

        if self.root_layout:
            self.remove_child(self.root_layout)

        self.root_layout = layout
        self.add_child(self.root_layout)
        self._arrange_content()
