from termui.layouts._layout import Layout
from termui.widgets._widget import Widget


class GridLayout(Layout):
    """A grid layout that arranges widgets in a grid format."""

    def __init__(self, *children: Widget | Layout, **kwargs) -> None:
        """Initialize the grid layout with the specified number of rows and columns."""
        super().__init__("GridLayout", *children, **kwargs)
        self.rows = (
            max(
                child.row[1] if isinstance(child.row, tuple) else child.row
                for child in self.children
            )
            if self.children
            else 0
        )
        self.cols = (
            max(
                child.col[1] if isinstance(child.col, tuple) else child.col
                for child in self.children
            )
            if self.children
            else 0
        )

    def calculate_minimum_size(self) -> tuple[int, int]:
        """Calculate the minimum size needed for the grid layout."""
        if not self.children:
            return 0, 0

        total_width = sum(child.region.width for child in self.children)
        total_width += self.spacing * (self.cols - 1)
        max_height = max(child.region.height for child in self.children) * self.rows

        return total_width, max_height

    def arrange(self) -> None:
        """Arrange the widgets in a grid format."""
        if not self.children:
            return

        min_width, min_height = self.calculate_minimum_size()

        if self.region.width < min_width:
            self.region.width = min_width
        if self.region.height < min_height:
            self.region.height = min_height

        row_height = self.region.height // self.rows
        col_width = self.region.width // self.cols

        for i, child in enumerate(self.children):
            row = i // self.cols
            row_span = (
                child.row[1] - child.row[0] if isinstance(child.row, tuple) else 1
            )
            col = i % self.cols
            col_span = (
                child.col[1] - child.col[0] if isinstance(child.col, tuple) else 1
            )
            x_offset = col * (col_width * col_span + self.spacing)
            y_offset = row * (row_height * row_span + self.spacing)

            child.set_position(self.region.x + x_offset, self.region.y + y_offset)
            child.set_size(col_width * col_span, row_height * row_span)

        self.mark_dirty()
