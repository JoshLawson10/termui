from termui.widgets.widget import Widget


class Text(Widget):
    """A widget that displays text."""

    def __init__(self, content: str | list[str]) -> None:
        super().__init__(name="Text")
        self.content: list[str] = content if isinstance(content, list) else [content]
        self.update_dimensions(
            width=max(len(line) for line in self.content), height=len(self.content)
        )

    def render(self) -> list[list[str]]:
        return [list(line) for line in self.content]
