from typing import Literal, Optional

from termui._context_manager import app
from termui.char import Char
from termui.color import Color
from termui.theme import PrimitiveColors
from termui.widget import Widget

LabelPosition = Literal["left", "right"]


class ProgressBar(Widget):
    """
    A widget that displays a progress bar.
    """

    def __init__(
        self,
        value: int = 0,
        max_value: int = 100,
        label: Optional[str] = None,
        label_pos: LabelPosition = "left",
        bar_color: PrimitiveColors = "primary",
        **kwargs,
    ):
        """Initialize the progress bar.

        Args:
            value: The initial value of the progress bar.
            max_value: The maximum value of the progress bar.
            label: The label displayed on the progress bar.
            label_pos: The position of the label on the progress bar.
            bar_color: The color of the progress bar.
        """
        super().__init__(**kwargs)

        self.label = label
        """The label displayed on the progress bar."""
        self.label_pos = label_pos
        """The position of the label on the progress bar."""
        self.bar_color = bar_color
        """The color of the progress bar."""

        self.max_value = max_value
        """The maximum value of the progress bar."""
        self.current_value = min(max(value, 0), max_value)
        """The current value of the progress bar."""

        self.set_size(*self.get_minimum_size())

    def get_minimum_size(self) -> tuple[int, int]:
        """Get the minimum size of the progress bar.

        Returns:
            A tuple (min_width, min_height) representing the minimum space
            required for the button including padding and borders.
        """
        label_len = len(self.label) if self.label else 0
        amount_len = len(f"{self.current_value}/{self.max_value}")
        min_width = label_len + amount_len + 2 if self.label else 0
        return min_width, 1

    def set_value(self, value: int) -> None:
        """Set the value of the progress bar.

        Args:
            value (int): The new value for the progress bar.
        """
        self.current_value = min(max(value, 0), self.max_value)
        self.mark_dirty()

    def increment(self, amount: int) -> None:
        """Increment the value of the progress bar.

        Args:
            amount (int): The amount to increment the progress bar by.
        """
        self.set_value(self.current_value + amount)

    def decrement(self, amount: int) -> None:
        """Decrement the value of the progress bar.

        Args:
            amount (int): The amount to decrement the progress bar by.
        """
        self.set_value(self.current_value - amount)

    def _get_colors(self) -> tuple[Color, Color]:
        """Get the colors of the progress bar.

        Returns:
            A tuple of the colors of the progress bar.
        """
        bar_color: Color = app.current_theme[self.bar_color]
        label_color: Color = app.current_theme["neutral_content"]

        return bar_color, label_color

    def render(self) -> list[list[Char]]:
        """Render the button to a 2D character array.

        Returns:
            A 2D list of Char objects representing the button's appearance
            with proper colors, borders, text, and visual effects.
        """
        bar_color, label_color = self._get_colors()

        bar_length = 40
        filled_length = int(bar_length * self.current_value // self.max_value)
        bar_string = (
            [Char("█", bar_color, None)] * filled_length
            + [Char("─", label_color, None)] * (bar_length - filled_length - 1)
            + [Char("┤", label_color, None)]
        )

        bar_label = (
            [Char(char, label_color, None) for char in self.label] if self.label else []
        )

        bar_amount = [
            Char(char, label_color, None)
            for char in f"{self.current_value}/{self.max_value}"
        ]

        space = [Char(" ", label_color, None)]

        match self.label_pos:
            case "left":
                return [bar_label + bar_string + space + bar_amount]
            case "right":
                return [bar_string + space + bar_amount + bar_label]
