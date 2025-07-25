from ._layout import BoxLayoutManager


class HorizontalLayoutManager(BoxLayoutManager):
    """Layout manager for horizontal arrangement."""

    def __init__(self, gap: int = 0, padding: tuple[int, int, int, int] = (0, 0, 0, 0)):
        super().__init__("horizontal", gap, padding)
