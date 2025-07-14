from termui.layouts.layout import Layout
from termui.widgets._widget import Widget


class HorizontalLayout(Layout):
    """A layout that arranges widgets horizontally."""

    def __init__(self, *children: Widget | Layout) -> None:
        super().__init__(*children)

    def arrange(self) -> None:
        if not self.children:
            return

        current_x: int = 0
        for child in self.children:
            self.add_placement(
                child=child,
                x_pos=current_x,
                y_pos=0,
                width=(
                    child.width
                    if hasattr(child, "width")
                    else self.width // len(self.children)
                ),
                height=self.height,
            )
            current_x += (
                child.width
                if hasattr(child, "width")
                else self.width // len(self.children)
            )
