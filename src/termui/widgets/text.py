from termui.widgets._widget import Widget
from termui.types.char import Char
from termui.colors.ansi import AnsiColor


class Text(Widget):
    """A widget that displays text."""

    def __init__(self, content: str | list[str], **kwargs) -> None:
        self.content: list[str] = content if isinstance(content, list) else [content]

        width = max(len(line) for line in self.content) if self.content else 0
        height = len(self.content)

        kwargs.setdefault("width", width)
        kwargs.setdefault("height", height)

        super().__init__(**kwargs)

        self.fg_color = kwargs.get("fg_color", AnsiColor.WHITE)
        self.bg_color = kwargs.get("bg_color", None)

    def set_content(self, content: str | list[str]) -> None:
        """Update the text content."""
        new_content = content if isinstance(content, list) else [content]
        if new_content != self.content:
            self.content = new_content

            new_width = max(len(line) for line in self.content) if self.content else 0
            new_height = len(self.content)

            if new_width != self.width or new_height != self.height:
                self.set_size(new_width, new_height)

            self.mark_dirty()

    def append_line(self, line: str) -> None:
        """Append a line to the text content."""
        self.content.append(line)
        new_width = max(len(line) for line in self.content)
        if new_width > self.width:
            self.width = new_width
        self.height = len(self.content)
        self.mark_dirty()

    def render(self) -> list[list[Char]]:
        """Render the text content."""
        rendered_content: list[list[Char]] = []

        for line in self.content:
            rendered_line: list[Char] = []
            for char in line:
                rendered_char = Char(char, self.fg_color, self.bg_color)
                rendered_line.append(rendered_char)

            while len(rendered_line) < self.width:
                rendered_line.append(Char(" ", self.fg_color, self.bg_color))

            rendered_content.append(rendered_line)

        while len(rendered_content) < self.height:
            empty_line = [
                Char(" ", self.fg_color, self.bg_color) for _ in range(self.width)
            ]
            rendered_content.append(empty_line)

        return rendered_content
