from termui.layout import Layout
from termui.widget import Widget


class VerticalLayout(Layout):
    """A layout that arranges widgets vertically."""

    def __init__(self, *children: Widget, **kwargs) -> None:
        super().__init__("VerticalLayout", *children, **kwargs)

    def calculate_minimum_size(self) -> tuple[int, int]:
        """Calculate minimum size needed for vertical layout."""
        if not self.children:
            return 0, 0

        max_width = (
            max(child.region.width for child in self.children) if self.children else 0
        )
        total_height = sum(child.region.height for child in self.children)
        total_height += self.spacing * max(0, len(self.children) - 1)

        return max_width, total_height

    def arrange(self) -> None:
        """Arrange the widgets vertically."""
        if not self.children:
            return

        min_width, min_height = self.calculate_minimum_size()

        if self.region.width < min_width:
            self.region.width = min_width
        if self.region.height < min_height:
            self.region.height = min_height

        y_offset = 0
        for child in self.children:
            child.set_position(self.region.x, self.region.y + y_offset)
            child.set_size(self.region.width, child.region.height)
            y_offset += child.region.height + self.spacing

        self.mark_dirty()
