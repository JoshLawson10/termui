from dataclasses import dataclass


@dataclass
class Size:
    """Represents the size of a terminal or a Div."""

    cols: int
    rows: int

    def __post_init__(self):
        if self.cols <= 0 or self.rows <= 0:
            raise ValueError("Size must have positive dimensions.")

    def __str__(self):
        return f"{self.cols}x{self.rows}"


@dataclass
class Region:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        if self.x < 0 or self.y < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError(
                "Region must have non-negative coordinates and positive dimensions."
            )

    def __str__(self):
        return (
            f"Region(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
        )

    def move(self, dx: int, dy: int) -> "Region":
        """Move the region by dx and dy."""
        self.x += dx
        self.y += dy
        return Region(self.x, self.y, self.width, self.height)
