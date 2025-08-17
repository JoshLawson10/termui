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
        """Initialize the Text widget with content and styling options.

        Args:
            content: The text content to display. Single strings become one line,
                    lists of strings become multiple lines.
            **kwargs: Widget configuration options:
                - name (str): Widget identifier, defaults to "Text"
                - fg_color (Color): Text color, defaults to white
                - bg_color (Color | None): Background color, defaults to None
                - width (int): Override automatic width calculation
                - height (int): Override automatic height calculation
                - Other widget properties (id, pos, etc.)
        """
        super().__init__(name=kwargs.get("name", "Text"), **kwargs)

        self.content: list[str] = content if isinstance(content, list) else [content]
        """The text content to display."""
        self.fg_color = kwargs.get("fg_color", Color(255, 255, 255))
        """The foreground color of the text."""
        self.bg_color = kwargs.get("bg_color", None)
        """The background color of the text."""

        self.set_size(*self.get_minimum_size())

    def get_minimum_size(self) -> tuple[int, int]:
        """Get the minimum size required to display the text content.

        Calculates the smallest possible dimensions that can accommodate all
        text without truncation.

        Returns:
            tuple[int, int]: Minimum (width, height) in characters.
        """
        if not self.content:
            return 1, 1
        width = max(len(line) for line in self.content)
        height = max(len(self.content), 1)
        return width, height

    def set_content(self, content: str | list[str]) -> None:
        """Update the text content and recalculate widget size.

        Changes the displayed text content and automatically adjusts the widget
        dimensions to fit the new content. Marks the widget as dirty to trigger
        re-rendering.

        Args:
            content: The new text content to display.
        """
        self.content = content if isinstance(content, list) else [content]
        self.mark_dirty()

    def render(self) -> list[list[Char]]:
        """Render the text with its border and children.

        Returns:
            list[list[Char]]: The rendered content of the text widget.
        """
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
