from termui.layouts.layout import Layout
from termui.widgets.base import Widget


class VerticalLayout(Layout):
    """A layout that arranges widgets vertically."""

    def __init__(self, *children: Widget | Layout) -> None:
        super().__init__(*children)

    def arrange(self) -> None:
        if not self.children:
            return

        current_y: int = 0
        for child in self.children:
            self.add_placement(
                child=child,
                x_pos=0,
                y_pos=current_y,
                width=self.width,
                height=(
                    child.height
                    if hasattr(child, "height")
                    else self.height // len(self.children)
                ),
            )
            current_y += (
                child.height
                if hasattr(child, "height")
                else self.height // len(self.children)
            )
            print(
                f"Placed {child} at ({0}, {current_y - child.height}) with width {self.width} and height {child.height}"
            )
