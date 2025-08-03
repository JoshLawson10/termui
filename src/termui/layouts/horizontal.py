from termui.layouts.layout import Layout
from termui.widgets._widget import Widget


class HorizontalLayout(Layout):
    """A layout that arranges widgets horizontally."""

    def __init__(self, *children: Widget | Layout) -> None:
        super().__init__(*children)

    def arrange(self) -> None:
        return
