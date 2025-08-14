from dataclasses import dataclass

from termui.errors import DimensionError


@dataclass
class Region:
    x: int
    y: int
    width: int
    height: int

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
        """Check if the point (x, y) is inside the region."""
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    def move_relative(self, dx: int, dy: int) -> "Region":
        """Move the region by dx and dy."""
        self.x += dx
        self.y += dy
        return Region(self.x, self.y, self.width, self.height)

    def move_absolute(self, x: int, y: int) -> "Region":
        self.x = x
        self.y = y
        return Region(self.x, self.y, self.width, self.height)

    def update_dimensions(self, new_width: int, new_height: int) -> "Region":
        self.width = new_width
        self.height = new_height
        return Region(self.x, self.y, self.width, self.height)

    def reset_position(self) -> "Region":
        """Reset the region's position to (0, 0) while keeping its size."""
        return Region(0, 0, self.width, self.height)
