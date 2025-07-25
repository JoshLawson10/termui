from ._layout import BoxLayoutManager


class VerticalLayoutManager(BoxLayoutManager):
    """Layout manager for vertical arrangement."""

    def __init__(self, gap: int = 0, padding: tuple[int, int, int, int] = (0, 0, 0, 0)):
        super().__init__("vertical", gap, padding)
