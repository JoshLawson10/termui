from termui.widgets.base import Widget


class Text(Widget):
    """A widget that displays text."""

    def __init__(self, content: str) -> None:
        super().__init__(name="Text")
        self.content: str = content

    def render(self) -> str:
        return self.content
