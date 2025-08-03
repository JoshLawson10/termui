from termui.layouts.layout import Layout
from termui.widgets._widget import Widget


class VerticalLayout(Layout):
    """A layout that arranges widgets vertically."""

    def __init__(self, *children: Widget | Layout) -> None:
        super().__init__(*children)

    def arrange(self) -> None:
        return
