from termui._context_manager import app
from termui.char import Char
from termui.color import Color
from termui.theme import PrimitiveColors
from termui.utils.align import HorizontalAlignment, get_aligned_start_x
from termui.widget import Widget


class Text(Widget):
    """A widget that displays text."""

    def __init__(
        self,
        content: str | list[str],
        text_color: PrimitiveColors = "neutral",
        background_color: PrimitiveColors | None = None,
        is_content: bool = False,
        align: HorizontalAlignment = "left",
        **kwargs,
    ) -> None:
        """Initialize the Text widget with content and styling options.

        Args:
            content: The text content to display. Single strings become one line,
                    lists of strings become multiple lines.
            fg_color: The foreground color of the text (default: white).
            bg_color: The background color of the text (default: None).
            align: The alignment of the text (default: left).
            **kwargs: Additional widget configuration options.
        """
        super().__init__(name=kwargs.get("name", "Text"), **kwargs)

        self.content: list[str] = content if isinstance(content, list) else [content]
        """The text content to display."""
        self.text_color: PrimitiveColors = text_color
        """The text color."""
        self.background_color: PrimitiveColors | None = background_color
        """The background color."""

        self.is_content: bool = is_content
        """Whether to use content color variants for the text color.

        i.e `neutral_content` instead of `neutral` if is_content is True.
        """

        self.align: HorizontalAlignment = align
        """How the content should be aligned horizontally."""

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

    def get_content(self) -> list[str]:
        """Get the current text content.

        Returns:
            list[str]: The current text content as a list of strings.
        """
        return self.content

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

    def _get_colors(self) -> tuple[Color, Color | None]:
        theme = app.current_theme

        text_color = theme[
            f"{self.text_color}_content" if self.is_content else self.text_color
        ]
        if self.background_color:
            background_color = theme[self.background_color]
        else:
            background_color = None

        return text_color, background_color

    def render(self) -> list[list[Char]]:
        """Render the text with its border and children.

        Returns:
            list[list[Char]]: The rendered content of the text widget.
        """
        rendered_content: list[list[Char]] = [[] for _ in range(self.region.height)]

        text_color, background_color = self._get_colors()

        for i in range(self.region.height):
            rendered_line: list[Char] = [Char("") for _ in range(self.region.width)]

            line = self.content[i] if i < len(self.content) else ""

            start_x = get_aligned_start_x(line, self.region.width, self.align)

            for j in range(self.region.width - start_x):
                char = line[j] if j < len(line) else " "
                rendered_char = Char(char, text_color, background_color)
                rendered_line[start_x + j] = rendered_char

            rendered_content[i] = rendered_line

        return rendered_content
