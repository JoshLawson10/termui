from dataclasses import dataclass
from typing import Callable, Literal, Optional

from termui._context_manager import app
from termui.char import Char
from termui.color import Color
from termui.events import MouseDown, MouseUp
from termui.theme import PrimitiveColors
from termui.utils.align import get_aligned_start_x, get_aligned_start_y
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from termui.widget import Widget

ButtonVariantType = Literal["solid", "outline", "rounded", "dashed"]
ButtonColorType = Literal[PrimitiveColors, "default"]
ButtonSizeType = Literal["icon", "small", "medium", "large"]

ButtonState = Literal["default", "hovered", "pressed", "disabled"]


@dataclass
class ButtonVariant:
    """Defines the visual style of a button (border and fill).

    Args:
        name: The style name identifier.
        border_style: The border style to use for drawing.
        fill_char: The character used to fill the button background.
    """

    name: ButtonVariantType
    border_style: BorderStyle
    fill_char: str


@dataclass
class ButtonSize:
    """Defines the size and padding of a button.

    Args:
        name: The size variant name identifier.
        padding_x: Horizontal padding inside the button.
        padding_y: Vertical padding inside the button.
    """

    name: ButtonSizeType
    padding_x: int
    padding_y: int


BUTTON_VARIANTS: dict[ButtonVariantType, ButtonVariant] = {
    "solid": ButtonVariant(name="solid", border_style="full", fill_char="█"),
    "outline": ButtonVariant(name="outline", border_style="solid", fill_char=" "),
    "rounded": ButtonVariant(name="rounded", border_style="round", fill_char=" "),
    "dashed": ButtonVariant(name="dashed", border_style="dashed", fill_char=" "),
}

BUTTON_SIZES: dict[ButtonSizeType, ButtonSize] = {
    "icon": ButtonSize(name="icon", padding_x=0, padding_y=0),
    "small": ButtonSize(name="small", padding_x=2, padding_y=0),
    "medium": ButtonSize(name="medium", padding_x=4, padding_y=1),
    "large": ButtonSize(name="large", padding_x=6, padding_y=2),
}


class Button(Widget):
    """A clickable button widget with customizable appearance and behavior.

    The Button widget supports various visual styles, colors, sizes, and states.
    It can display text and respond to mouse clicks with configurable callbacks.
    """

    def __init__(
        self,
        *,
        variant: ButtonVariantType = "solid",
        color: ButtonColorType = "default",
        size: ButtonSizeType = "small",
        disabled: bool = False,
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
        on_click: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        """Initialize a button with specified label and styling.

        Args:
            label: The text displayed on the button.
            variant: Visual style of the button. One of `solid`, `outline`, `rounded`, `dashed`.
            color: Colour of the button. See ___ for universal colours.
            size: Size of the button. One of `icon`, `small`, `medium`, `large`.
            disabled: Whether the button is disabled and non-interactive.
            padding: Additional padding around the button as (top, right, bottom, left).
            on_click: Callback function executed when the button is clicked.
            **kwargs: Additional widget arguments passed to the parent constructor.
        """
        super().__init__(**kwargs)

        self.variant: ButtonVariant = BUTTON_VARIANTS.get(variant, "default")
        """Style of the button."""
        self.color = color
        """Color of the button."""
        self.size: ButtonSize = BUTTON_SIZES.get(size, "small")
        """Size of the button."""

        self.padding = padding
        """Padding to apply around the button's content."""
        self.disabled = disabled
        """Whether the button is disabled and non-interactive."""
        self.on_click = on_click or (lambda: None)
        """Callback function executed when the button is clicked."""

        self.content: str = ""
        """The text displayed on the button.

        This is initialised in __call__.
        """

        self.state: ButtonState = "default"
        """Current state of the button."""

        self.set_size(*self.get_minimum_size())

    def __call__(
        self,
        content: str,
    ) -> "Button":
        """Make the widget callable to accept children.

        Args:
            content: Content for the button

        Returns:
            Self, to allow method chaining and use in layouts.
        """
        self.content = content
        self.region.width, self.region.height = self.get_minimum_size()
        return self

    def _get_colors(self) -> tuple[Color, Color | None]:
        """Parse and return the button color variants from the current theme."""
        fg: Color = Color(0, 0, 0)
        bg: Color | None = None

        theme = app.current_theme

        match self.variant:
            case "solid":
                fg = theme[f"{self.color}_content"]
                bg = theme[self.color]
            case "outline":
                fg = theme[self.color]
                bg = None
            case "rounded":
                fg = theme[self.color]
                bg = None
            case "dashed":
                fg = theme[self.color]
                bg = None
            case _:
                fg = theme[f"{self.color}_content"]
                bg = theme[self.color]

        match self.state:
            case "hovered":
                return fg.darken(0.2), bg.lighten(0.2)
            case "pressed":
                return fg.darken(0.2), bg.darken(0.2)
            case "disabled":
                return fg.darken(0.5), bg.darken(0.5)
            case _:
                return fg, bg

    def get_minimum_size(self) -> tuple[int, int]:
        """Calculate the minimum size needed to display the button.

        Returns:
            A tuple (min_width, min_height) representing the minimum space
            required for the button including padding and borders.
        """
        min_width = (
            len(self.content)
            + self.size.padding_x * 2
            + self.padding[1]
            + self.padding[3]
            + 2
        )
        min_height = 3 + self.size.padding_y * 2 + self.padding[0] + self.padding[2]
        return max(min_width, 1), max(min_height, 1)

    def render(self) -> list[list[Char]]:
        """Render the button to a 2D character array.

        Returns:
            A 2D list of Char objects representing the button's appearance
            with proper colors, borders, text, and visual effects.
        """

        fg, bg = self._get_colors()

        self.region.width, self.region.height = self.get_minimum_size()

        box_model: list[list[Char]] = draw_rectangle(
            self.region.width,
            self.region.height,
            border_style=self.variant.border_style,
            border_color=bg,
            fill=Char(self.variant.fill_char, bg, None),
        )

        depth_char_top = ""
        depth_char_bottom = ""

        if self.variant.name == "solid":
            match self.size.name:
                case "icon":
                    depth_char_top = "█"
                    depth_char_bottom = "▂"
                case "small":
                    depth_char_top = "▆"
                    depth_char_bottom = "▂"
                case "medium":
                    depth_char_top = "▅"
                    depth_char_bottom = "▃"
                case "large":
                    depth_char_top = "▅"
                    depth_char_bottom = "▃"
            for char in box_model[0]:
                char.char = depth_char_top
                char.bg_color = bg.lighten(0.1)
            for char in box_model[-1]:
                char.char = depth_char_bottom
                char.fg_color = bg.darken(0.1)
                char.bg_color = bg

        text_line: list[Char] = [Char(c, fg, bg) for c in self.content]

        text_start_x = get_aligned_start_x(
            self.content,
            self.region.width - self.padding[1] - self.padding[3],
            "center",
        )
        text_start_y = get_aligned_start_y(self.region.height, "middle")

        for i, char in enumerate(text_line):
            box_model[text_start_y][text_start_x + i] = char

        return box_model

    def click(self) -> None:
        """Programmatically trigger a button click.

        Executes the button's click callback if the button is not disabled.
        """
        if self.disabled:
            return
        self.on_click()

    def _on_mouse_enter(self) -> None:
        """Handle mouse enter events by changing to hovered state."""
        self.state = "hovered"
        self.mark_dirty()

    def _on_mouse_exit(self) -> None:
        """Handle mouse exit events by returning to default state."""
        self.state = "default"
        self.mark_dirty()

    def _on_mouse_down(self, event: MouseDown) -> None:
        """Handle mouse down events by changing to pressed state and triggering click."""
        if self.disabled:
            return
        self.state = "pressed"
        self.click()
        self.mark_dirty()

    def _on_mouse_up(self, event: MouseUp) -> None:
        """Handle mouse up events by changing to hovered state.

        Args:
            event (MouseUp): The mouse event.
        """

        if self.disabled:
            return
        self.state = "default"
        self.mark_dirty()
