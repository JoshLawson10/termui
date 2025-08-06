from termui.layouts._layout import Layout
from termui.widgets._widget import Widget


class VerticalLayout(Layout):
    """A layout that arranges widgets vertically."""

    def __init__(self, *children: Widget | Layout) -> None:
        super().__init__("VerticalLayout", *children)

    def arrange(self) -> None:
        """Arrange the widgets vertically."""
        y_offset = 0
        for child in self.children:
            child.set_position(self.region.x, self.region.y + y_offset)
            y_offset += child.region.height
