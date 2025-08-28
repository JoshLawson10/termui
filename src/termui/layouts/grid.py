from termui.errors import LayoutError
from termui.layout import Layout
from termui.widget import Widget


class GridLayout(Layout):
    """A grid layout that arranges widgets in a grid format.

    The GridLayout positions widgets in a two-dimensional grid based on their
    'grid_pos' attribute. Widgets can span multiple rows and/or columns. The grid
    automatically calculates cell sizes and distributes available space.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize the grid layout with child widgets.

        Args:
            **kwargs: Additional layout options including spacing.
        """
        self.grid_map: dict[tuple[int, int], Widget] = {}
        """A mapping of grid positions to their corresponding widgets."""
        self.span_map: dict[Widget, tuple[int, int, int, int]] = (
            {}
        )  # widget -> (row, col, row_span, col_span)
        """A mapping of widgets to their grid positions and spans."""

        super().__init__(name="GridLayout", **kwargs)

    def calculate_minimum_size(self) -> tuple[int, int]:
        return super().calculate_minimum_size()

    def _add_child_to_span_map(self, child: Widget) -> None:
        """
        Add a child widget to the span map for grid positioning.

        Args:
            child: The child widget to add.

        Raises:
            LayoutError: If the child widget's position overlaps with existing widgets.
        """
        if child in self.grid_map or child in self.span_map:
            return

        child_row, child_col = child.grid_pos

        # Handle row specification
        if isinstance(child_row, tuple):
            row = child_row[0]
            row_span = child_row[1] - child_row[0] + 1
        else:
            row = child_row
            row_span = 1

        # Handle column specification
        if isinstance(child_col, tuple):
            col = child_col[0]
            col_span = child_col[1] - child_col[0] + 1
        else:
            col = child_col
            col_span = 1

        # Convert to 0-based indexing
        row_0_index = row - 1
        col_0_index = col - 1

        # Check for overlaps and populate grid_map
        for r in range(row_0_index, row_0_index + row_span):
            for c in range(col_0_index, col_0_index + col_span):
                if (r, c) in self.grid_map:
                    raise LayoutError(
                        f"Trying to place widget {child.name} at grid position ({r}, {c}). "
                        f"Already occupied by {self.grid_map[(r, c)].name}. "
                        f"Row: {row}, Col: {col}, Row Span: {row_span}, Col Span: {col_span}"
                    )
                self.grid_map[(r, c)] = child

        self.span_map[child] = (row_0_index, col_0_index, row_span, col_span)
        child.set_position(0, 0)  # Initial position; will be updated in arrange()

    def _add_children_to_span_map(self, *children: Widget) -> None:
        """Recursively adds child widgets to the span map.

        Args:
            *children: The child widgets to add.
        """
        for child in children:
            self._add_child_to_span_map(child)

    def _calculate_grid_dimensions(self) -> tuple[int, int]:
        """Calculate the required grid dimensions based on widget positions.

        Returns:
            A tuple (max_rows, max_cols) representing the minimum grid size
            needed to accommodate all widgets.
        """
        if not self.grid_map:
            return 1, 1

        max_row = max(pos[0] for pos in self.grid_map) + 1
        max_col = max(pos[1] for pos in self.grid_map) + 1

        return max_row, max_col

    def _calculate_cell_sizes(
        self, max_rows: int, max_cols: int
    ) -> tuple[list[int], list[int]]:
        """Calculate the size of each row and column based on content.

        Args:
            max_rows: The number of rows in the grid.
            max_cols: The number of columns in the grid.

        Returns:
            A tuple (row_heights, col_widths) where each list contains the
            calculated size for each row/column.
        """
        row_heights = [0] * max_rows
        col_widths = [0] * max_cols

        # Calculate minimum sizes based on widget content
        for widget, (row, col, row_span, col_span) in self.span_map.items():
            if hasattr(widget, "get_minimum_size"):
                min_width, min_height = widget.get_minimum_size()
            else:
                min_width, min_height = widget.region.width, widget.region.height

            # For single-cell widgets, update the cell size directly
            if row_span == 1 and col_span == 1:
                row_heights[row] = max(row_heights[row], min_height)
                col_widths[col] = max(col_widths[col], min_width)
            else:
                # For spanning widgets, distribute size across cells
                # This is a simplified approach - you might want more sophisticated distribution
                height_per_cell = min_height // row_span
                width_per_cell = min_width // col_span

                for r in range(row, row + row_span):
                    row_heights[r] = max(row_heights[r], height_per_cell)
                for c in range(col, col + col_span):
                    col_widths[c] = max(col_widths[c], width_per_cell)

        # Ensure minimum cell sizes
        row_heights = [max(h, 1) for h in row_heights]
        col_widths = [max(w, 1) for w in col_widths]

        return row_heights, col_widths

    def _calculate_minimum_size(self) -> tuple[int, int]:
        """Calculate minimum size needed for the grid layout.

        Returns:
            A tuple (min_width, min_height) representing the minimum space
            required to display all widgets with proper spacing.
        """
        max_rows, max_cols = self._calculate_grid_dimensions()
        row_heights, col_widths = self._calculate_cell_sizes(max_rows, max_cols)

        total_width = sum(col_widths) + (self.spacing * max(0, max_cols - 1))
        total_height = sum(row_heights) + (self.spacing * max(0, max_rows - 1))

        return total_width, total_height

    def arrange(self) -> None:
        """Arrange the widgets in the grid."""
        if not self.children:
            return

        self._add_children_to_span_map(*self.children)

        max_rows, max_cols = self._calculate_grid_dimensions()
        row_heights, col_widths = self._calculate_cell_sizes(max_rows, max_cols)

        # Calculate minimum size
        min_width, min_height = self._calculate_minimum_size()

        # Ensure grid is at least minimum size
        self.region.width = max(self.region.width, min_width)
        self.region.height = max(self.region.height, min_height)

        # Distribute extra space
        total_spacing_width = self.spacing * max(0, max_cols - 1)
        total_spacing_height = self.spacing * max(0, max_rows - 1)

        available_width = self.region.width - total_spacing_width
        available_height = self.region.height - total_spacing_height

        total_min_width = sum(col_widths)
        total_min_height = sum(row_heights)

        extra_width = max(0, available_width - total_min_width)
        if extra_width > 0 and max_cols > 0:
            extra_per_col = extra_width // max_cols
            remainder_width = extra_width % max_cols
            for i in range(max_cols):
                col_widths[i] += extra_per_col
                if i < remainder_width:
                    col_widths[i] += 1

        extra_height = max(0, available_height - total_min_height)
        if extra_height > 0 and max_rows > 0:
            extra_per_row = extra_height // max_rows
            remainder_height = extra_height % max_rows
            for i in range(max_rows):
                row_heights[i] += extra_per_row
                if i < remainder_height:
                    row_heights[i] += 1

        # Calculate row and column positions
        row_positions = [0]
        for i, height in enumerate(row_heights[:-1]):
            row_positions.append(row_positions[-1] + height + self.spacing)

        col_positions = [0]
        for i, width in enumerate(col_widths[:-1]):
            col_positions.append(col_positions[-1] + width + self.spacing)

        # Position each widget
        positioned_widgets = set()
        for widget, (row, col, row_span, col_span) in self.span_map.items():
            if widget in positioned_widgets:
                continue

            # Calculate widget position
            x = self.region.x + col_positions[col]
            y = self.region.y + row_positions[row]

            # Calculate widget size (sum of spanned cells plus spacing)
            width = sum(col_widths[col : col + col_span])
            if col_span > 1:
                width += self.spacing * (col_span - 1)

            height = sum(row_heights[row : row + row_span])
            if row_span > 1:
                height += self.spacing * (row_span - 1)

            # Set widget position and size
            widget.set_position(x, y)
            widget.set_size(width, height)

            positioned_widgets.add(widget)

        self.mark_dirty()
