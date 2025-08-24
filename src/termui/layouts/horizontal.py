from termui.layout import Layout
from termui.widget import Widget


class HorizontalLayout(Layout):
    """A layout that arranges widgets horizontally."""

    def __init__(self, *children: Widget | Layout, **kwargs) -> None:
        super().__init__(name="HorizontalLayout", *children, **kwargs)

    def calculate_minimum_size(self) -> tuple[int, int]:
        """Calculate minimum size needed for horizontal layout."""
        if not self.children:
            return 0, 0

        total_width = sum(child.region.width for child in self.children)
        total_width += self.spacing * max(0, len(self.children) - 1)
        max_height = (
            max(child.region.height for child in self.children) if self.children else 0
        )

        return total_width, max_height

    def arrange(self) -> None:
        """Arrange the widgets horizontally."""
        if not self.children:
            return

        min_width, min_height = self.calculate_minimum_size()

        self.region.width = max(self.region.width, min_width)
        self.region.height = max(self.region.height, min_height)

        x_offset = 0
        for child in self.children:
            child.set_position(self.region.x + x_offset, self.region.y)
            child.set_size(child.region.width, self.region.height)
            x_offset += child.region.width + self.spacing

        self.mark_dirty()
