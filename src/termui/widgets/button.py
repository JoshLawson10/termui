from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional

from termui.char import Char
from termui.color import Color
from termui.events import MouseEvent
from termui.utils.align import get_aligned_start_x, get_aligned_start_y
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from termui.widget import Widget


type ButtonStyle = Literal["solid", "soft", "outline", "rounded", "dashed"]
"""Defines the visual style of a button."""
type ButtonColor = Literal[
    "default", "primary", "secondary", "accent", "info", "success", "warning", "error"
]
"""Defines the color scheme of a button."""
type ButtonSize = Literal["icon", "small", "medium", "large"]
"""Defines the size of a button."""
type ButtonState = Literal["default", "hovered", "pressed", "disabled"]
"""Defines the state of a button."""


@dataclass
class ButtonVariant:
    """Base class for button style variants."""

    name: ButtonStyle | ButtonColor | ButtonSize


@dataclass
class ButtonStyleVariant(ButtonVariant):
    """Defines the visual style of a button (border and fill).

    Args:
        name: The style name identifier.
        border_style: The border style to use for drawing.
        fill_char: The character used to fill the button background.
    """

    border_style: BorderStyle
    fill_char: str


@dataclass
class ButtonColorVariant(ButtonVariant):
    """Defines the color scheme of a button.

    Args:
        name: The color scheme name identifier.
        fg_color: The foreground color for text and borders.
        bg_color: The background color for the button.
    """

    fg_color: Color
    bg_color: Color


@dataclass
class ButtonSizeVariant(ButtonVariant):
    """Defines the size and padding of a button.

    Args:
        name: The size variant name identifier.
        padding_x: Horizontal padding inside the button.
        padding_y: Vertical padding inside the button.
    """

    padding_x: int
    padding_y: int


BUTTON_STYLES: dict[ButtonStyle, ButtonStyleVariant] = {
    "solid": ButtonStyleVariant(name="solid", border_style="full", fill_char="█"),
    "soft": ButtonStyleVariant(name="soft", border_style="full", fill_char="░"),
    "outline": ButtonStyleVariant(name="outline", border_style="solid", fill_char=" "),
    "rounded": ButtonStyleVariant(name="rounded", border_style="round", fill_char=" "),
    "dashed": ButtonStyleVariant(name="dashed", border_style="dashed", fill_char=" "),
}

BUTTON_COLORS: dict[ButtonColor, ButtonColorVariant] = {
    "default": ButtonColorVariant(
        name="default",
        fg_color=Color(227, 227, 230),
        bg_color=Color(21, 24, 29),
    ),
    "primary": ButtonColorVariant(
        name="primary",
        fg_color=Color(237, 241, 253),
        bg_color=Color(96, 93, 246),
    ),
    "secondary": ButtonColorVariant(
        name="secondary",
        fg_color=Color(246, 228, 240),
        bg_color=Color(224, 68, 150),
    ),
    "accent": ButtonColorVariant(
        name="accent",
        fg_color=Color(33, 76, 73),
        bg_color=Color(80, 206, 188),
    ),
    "info": ButtonColorVariant(
        name="info",
        fg_color=Color(18, 45, 71),
        bg_color=Color(76, 183, 248),
    ),
    "success": ButtonColorVariant(
        name="success",
        fg_color=Color(27, 75, 58),
        bg_color=Color(83, 206, 149),
    ),
    "warning": ButtonColorVariant(
        name="warning",
        fg_color=Color(112, 53, 20),
        bg_color=Color(242, 186, 24),
    ),
    "error": ButtonColorVariant(
        name="error",
        fg_color=Color(70, 10, 24),
        bg_color=Color(240, 109, 128),
    ),
}

BUTTON_SIZES: dict[ButtonSize, ButtonSizeVariant] = {
    "icon": ButtonSizeVariant(name="icon", padding_x=0, padding_y=0),
    "small": ButtonSizeVariant(name="small", padding_x=2, padding_y=0),
    "medium": ButtonSizeVariant(name="medium", padding_x=4, padding_y=1),
    "large": ButtonSizeVariant(name="large", padding_x=6, padding_y=2),
}


class Button(Widget):
    """A clickable button widget with customizable appearance and behavior.

    The Button widget supports various visual styles, colors, sizes, and states.
    It can display text and respond to mouse clicks with configurable callbacks.
    """

    def __init__(
        self,
        label: str,
        style: str = "solid default icon",
        *,
        disabled: bool = False,
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
        on_click: Optional[Callable[[], None]] = None,
        state: ButtonState = "default",
        **kwargs,
    ) -> None:
        """Initialize a button with specified label and styling.

        Args:
            label: The text displayed on the button.
            style: Space-separated style string combining ButtonStyle, ButtonColor, and ButtonSize
            disabled: Whether the button is disabled and non-interactive.
            padding: Additional padding around the button as (top, right, bottom, left).
            on_click: Callback function executed when the button is clicked.
            state: Current visual state of the button.
            **kwargs: Additional widget arguments passed to the parent constructor.
        """
        super().__init__(name=kwargs.get("name", f"Button-{label}"), **kwargs)

        self.label = label
        """The text label displayed on the button."""
        self.padding = padding
        """Padding to apply around the button's content."""
        self.disabled = disabled
        """Whether the button is disabled and non-interactive."""
        self.on_click = on_click or (lambda: None)
        """Callback function executed when the button is clicked."""

        self.style, self.color, self.size = self._get_styles(style)
        """Visual style, color scheme, and size of the button."""
        self.state: ButtonState = state
        """Current state of the button."""

        self.set_size(*self.get_minimum_size())

    def __call__(
        self,
        *,
        label: Optional[str] = None,
        style: str = "solid default icon",
        disabled: Optional[bool] = None,
        padding: Optional[tuple[int, int, int, int]] = None,
        on_click: Optional[Callable[[], None]] = None,
        state: Optional[ButtonState] = None,
    ) -> "Button":
        """Make the widget callable to accept children.

        This allows syntax like:
        ```python
        MyButton = Button(
            "My Button",
            "accent small",
            disabled=True
        )

        return MyButton(label="My Custom Button")
        ```

        Args:
            label: The text displayed on the button.
            style: Space-separated style string combining ButtonStyle, ButtonColor, and ButtonSize
            disabled: Whether the button is disabled and non-interactive.
            padding: Additional padding around the button as (top, right, bottom, left).
            on_click: Callback function executed when the button is clicked.
            state: Current visual state of the button.

        Returns:
            Self, to allow method chaining and use in layouts.
        """
        self.label = label if label else self.label
        self.style, self.color, self.size = (
            self._get_styles(style) if style else (self.style, self.color, self.size)
        )
        self.disabled = disabled if disabled else self.disabled
        self.padding = padding if padding else self.padding
        self.on_click = on_click if on_click else self.on_click
        self.state = state if state else self.state
        return self

    def _get_styles(
        self, style: str
    ) -> tuple[ButtonStyleVariant, ButtonColorVariant, ButtonSizeVariant]:
        """Parse and return the button style variants from a style string.

        Args:
            style: Space-separated string of style keywords.

        Returns:
            A tuple containing (style_variant, color_variant, size_variant)
            with defaults applied for any missing components.
        """
        button_style = BUTTON_STYLES["solid"]
        button_color = BUTTON_COLORS["default"]
        button_size = BUTTON_SIZES["medium"]
        for style in style.split(" "):
            if style in BUTTON_STYLES:
                button_style = BUTTON_STYLES[style]
            if style in BUTTON_COLORS:
                button_color = BUTTON_COLORS[style]
            if style in BUTTON_SIZES:
                button_size = BUTTON_SIZES[style]
        return button_style, button_color, button_size

    def _get_colors(self) -> tuple[Color, Color, Color, Color | None]:
        """Calculate the current colors based on style and state.

        Returns:
            A tuple (border_fg, border_bg, text_fg, text_bg) containing
            the colors to use for rendering the button in its current state.
        """
        fg = self.color.fg_color
        bg = self.color.bg_color
        text_fg = fg
        text_bg = bg

        match self.style:
            case "solid":
                text_fg = fg
                text_bg = bg
            case "soft":
                text_fg = fg.lighten(0.1)
                text_bg = bg.darken(0.1)
            case "outline":
                text_fg = bg
                text_bg = None
            case "rounded":
                text_fg = bg
                text_bg = None
            case "dashed":
                text_fg = fg
                text_bg = None

        match self.state:
            case "default":
                pass
            case "hovered":
                fg = fg.darken(0.2)
                bg = bg.lighten(0.2)
                text_fg = fg.lighten(0.2)
                text_bg = bg
            case "pressed":
                fg = fg.darken(0.2)
                bg = bg.darken(0.2)
                text_fg = fg.lighten(0.2)
                text_bg = bg
            case "disabled":
                fg = fg.darken(0.5)
                bg = bg.darken(0.5)
                text_fg = fg
                text_bg = bg

        return fg, bg, text_fg, text_bg

    def get_minimum_size(self) -> tuple[int, int]:
        """Calculate the minimum size needed to display the button.

        Returns:
            A tuple (min_width, min_height) representing the minimum space
            required for the button including padding and borders.
        """
        min_width = (
            len(self.label)
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

        fg, bg, text_fg, text_bg = self._get_colors()

        content: list[list[Char]] = draw_rectangle(
            self.region.width,
            self.region.height,
            border_style=self.style.border_style,
            border_color=bg,
            fill=Char(self.style.fill_char, bg, None),
        )

        if self.style.name == "solid" or self.style.name == "soft":
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
            for char in content[0]:
                char.char = depth_char_top
                char.bg_color = bg.lighten(0.1)
            for char in content[-1]:
                char.char = depth_char_bottom
                char.fg_color = bg.darken(0.1)
                char.bg_color = bg

        text_line: list[Char] = [Char(c, text_fg, text_bg) for c in self.label]

        text_start_x = get_aligned_start_x(
            self.label,
            self.region.width - self.padding[1] - self.padding[3],
            "center",
        )
        text_start_y = get_aligned_start_y(self.region.height, "middle")

        for i, char in enumerate(text_line):
            content[text_start_y][text_start_x + i] = char

        return content

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

    def _on_mouse_exit(self) -> None:
        """Handle mouse exit events by returning to default state."""
        self.state = "default"

    def _on_click(self, event: MouseEvent) -> None:
        """Handle mouse click events.

        Args:
            event: The mouse event that triggered the click.
        """
        self.state = "pressed"
        self.click()
