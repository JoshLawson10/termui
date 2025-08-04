from termui.layouts._layout import Layout
from termui.widgets._widget import Widget


class HorizontalLayout(Layout):
    """A layout that arranges widgets horizontally."""

    def __init__(self, *children: Widget | Layout) -> None:
        super().__init__("HorizontalLayout", *children)

    def arrange(self) -> None:
        """Arrange the widgets horizontally."""
        x_offset = 0
        for child in self.children:
            child.set_position(self.region.x + x_offset, self.region.y)
            x_offset += child.region.width
