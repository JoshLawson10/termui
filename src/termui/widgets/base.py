class Widget:
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: str) -> None:
        self.name = name

    def render(self) -> None:
        """Render the widget."""
        pass
