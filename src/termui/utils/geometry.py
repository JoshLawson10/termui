from dataclasses import dataclass

from termui.errors import DimensionError


@dataclass
class Region:
    x: int
    y: int
    """Position of the region"""
    width: int
    height: int
    """Dimensions of the region"""

    def __post_init__(self):
        if self.x < 0 or self.y < 0:
            raise DimensionError(
                f"Region coordinates ({self.x}, {self.y}) are negative. Region must have non-negative coordinates."
            )

        if self.width < 0 or self.height < 0:
            raise DimensionError(
                f"Region dimensions ({self.width}, {self.height}) are non-positive. Region must have positive dimensions."
            )

    def __str__(self):
        return (
            f"Region(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
        )

    def contains(self, x: int, y: int) -> bool:
        """Check if the point (x, y) is inside the region.

        Args:
            x: The x-coordinate of the point.
            y: The y-coordinate of the point.

        Returns:
            True if the point is inside the region, False otherwise.
        """
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    def move_relative(self, dx: int, dy: int) -> "Region":
        """Move the region by dx and dy.

        Args:
            dx: The amount to move the region along the x-axis.
            dy: The amount to move the region along the y-axis.

        Returns:
            A new Region instance representing the moved region.
        """
        self.x += dx
        self.y += dy
        return Region(self.x, self.y, self.width, self.height)

    def move_absolute(self, x: int, y: int) -> "Region":
        """Move the region to the absolute position (x, y).

        Args:
            x: The new x-coordinate of the region.
            y: The new y-coordinate of the region.

        Returns:
            A new Region instance representing the moved region.
        """
        self.x = x
        self.y = y
        return Region(self.x, self.y, self.width, self.height)

    def update_dimensions(self, new_width: int, new_height: int) -> "Region":
        """Update the dimensions of the region.

        Args:
            new_width: The new width of the region.
            new_height: The new height of the region.

        Returns:
            A new Region instance representing the updated region.
        """
        self.width = new_width
        self.height = new_height
        return Region(self.x, self.y, self.width, self.height)

    def reset_position(self) -> "Region":
        """Reset the region's position to (0, 0) while keeping its size.

        Returns:
            A new Region instance representing the reset region.
        """
        return Region(0, 0, self.width, self.height)
