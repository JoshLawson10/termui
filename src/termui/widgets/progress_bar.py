from typing import Literal, Optional

from termui.char import Char
from termui.color import Color
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
        label_color: Color = Color(255, 255, 255),
        fg_color: Color = Color(255, 255, 255),
        bg_color: Optional[Color] = None,
        **kwargs,
    ):
        """Initialize the progress bar.

        Args:
            value (int): The initial value of the progress bar.
            max_value (int): The maximum value of the progress bar.
            label (str, optional): The label displayed on the progress bar.
            label_pos (LabelPosition, optional): The position of the label on the progress bar.
            label_color (Color, optional): The color of the label text.
            fg_color (Color, optional): The foreground color of the progress bar.
            bg_color (Color, optional): The background color of the progress bar.
        """
        super().__init__(**kwargs)

        self.label = label
        """The label displayed on the progress bar."""
        self.label_pos = label_pos
        """The position of the label on the progress bar."""
        self.label_color = label_color
        """The color of the label text."""

        self.max_value = max_value
        """The maximum value of the progress bar."""
        self.current_value = min(max(value, 0), max_value)
        """The current value of the progress bar."""

        self.fg_color = fg_color
        """The foreground color of the progress bar."""
        self.bg_color = bg_color
        """The background color of the progress bar."""

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

    def render(self) -> list[list[Char]]:
        """Render the button to a 2D character array.

        Returns:
            A 2D list of Char objects representing the button's appearance
            with proper colors, borders, text, and visual effects.
        """
        bar_length = 40
        filled_length = int(bar_length * self.current_value // self.max_value)
        bar_string = (
            [Char("█", self.fg_color, self.bg_color)] * filled_length
            + [Char("─", Color(255, 255, 255), self.bg_color)]
            * (bar_length - filled_length - 1)
            + [Char("┤", Color(255, 255, 255), self.bg_color)]
        )

        bar_label = (
            [Char(char, self.label_color, self.bg_color) for char in self.label]
            if self.label
            else []
        )

        bar_amount = [
            Char(char, self.label_color, self.bg_color)
            for char in f"{self.current_value}/{self.max_value}"
        ]

        space = [Char(" ", self.label_color, self.bg_color)]

        match self.label_pos:
            case "left":
                return [bar_label + bar_string + space + bar_amount]
            case "right":
                return [bar_string + space + bar_amount + bar_label]
            case _:
                return [bar_label + bar_string + space + bar_amount]
