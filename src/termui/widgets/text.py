from termui.char import Char
from termui.color import Color

from termui.widget import Widget


class Text(Widget):
    """A widget that displays text."""

    def __init__(
        self,
        content: str | list[str],
        **kwargs,
    ) -> None:
        super().__init__(name=kwargs.get("name", "Text"), **kwargs)
        self.content: list[str] = content if isinstance(content, list) else [content]
        self.fg_color = kwargs.get("fg_color", Color(255, 255, 255))
        self.bg_color = kwargs.get("bg_color", None)

        if "width" not in kwargs or "height" not in kwargs:
            self._calculate_size()

    def _calculate_size(self) -> None:
        """Calculate the size based on content."""
        if not self.content:
            self.set_size(1, 1)
            return

        width = max(len(line) for line in self.content) if self.content else 1
        height = len(self.content)
        self.set_size(width, height)

    def get_minimum_size(self) -> tuple[int, int]:
        """Get minimum size needed for the text content."""
        if not self.content:
            return 1, 1
        width = max(len(line) for line in self.content)
        height = len(self.content)
        return width, height

    def set_content(self, content: str | list[str]) -> None:
        """Update the text content."""
        self.content = content if isinstance(content, list) else [content]
        self._calculate_size()
        self.mark_dirty()

    def render(self) -> list[list[Char]]:
        rendered_content: list[list[Char]] = []

        for i in range(self.region.height):
            rendered_line: list[Char] = []

            line = self.content[i] if i < len(self.content) else ""

            for j in range(self.region.width):
                char = line[j] if j < len(line) else " "
                rendered_char = Char(char, self.fg_color, self.bg_color)
                rendered_line.append(rendered_char)

            rendered_content.append(rendered_line)

        return rendered_content
