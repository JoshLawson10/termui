class Widget:
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.width: int = 0
        self.height: int = 0

    def update_dimensions(self, width: int, height: int) -> None:
        """Update the dimensions of the widget."""
        self.width = width
        self.height = height

    def render(self) -> None:
        """Render the widget."""
        pass
