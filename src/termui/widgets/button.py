from dataclasses import dataclass

from typing import Callable, Literal, Optional

from termui.colors import RGBColor
from termui.types.char import Char
from termui.utils.align import get_aligned_start_x, get_aligned_start_y
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle

from termui.widgets._widget import Widget


type ButtonStyle = Literal["solid", "soft", "outline", "rounded", "dashed"]
type ButtonColor = Literal[
    "default", "primary", "secondary", "accent", "info", "success", "warning", "error"
]
type ButtonSize = Literal["icon", "small", "medium", "large"]
type ButtonState = Literal["default", "selected", "pressed", "disabled"]


@dataclass
class ButtonVariant:
    name: ButtonStyle | ButtonColor | ButtonSize


@dataclass
class ButtonStyleVariant(ButtonVariant):
    border_style: BorderStyle
    fill_char: str


@dataclass
class ButtonColorVariant(ButtonVariant):
    fg_color: RGBColor
    bg_color: RGBColor


@dataclass
class ButtonSizeVariant(ButtonVariant):
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
        fg_color=RGBColor(227, 227, 230),
        bg_color=RGBColor(21, 24, 29),
    ),
    "primary": ButtonColorVariant(
        name="primary",
        fg_color=RGBColor(237, 241, 253),
        bg_color=RGBColor(96, 93, 246),
    ),
    "secondary": ButtonColorVariant(
        name="secondary",
        fg_color=RGBColor(246, 228, 240),
        bg_color=RGBColor(224, 68, 150),
    ),
    "accent": ButtonColorVariant(
        name="accent",
        fg_color=RGBColor(33, 76, 73),
        bg_color=RGBColor(80, 206, 188),
    ),
    "info": ButtonColorVariant(
        name="info",
        fg_color=RGBColor(18, 45, 71),
        bg_color=RGBColor(76, 183, 248),
    ),
    "success": ButtonColorVariant(
        name="success",
        fg_color=RGBColor(27, 75, 58),
        bg_color=RGBColor(83, 206, 149),
    ),
    "warning": ButtonColorVariant(
        name="warning",
        fg_color=RGBColor(112, 53, 20),
        bg_color=RGBColor(242, 186, 24),
    ),
    "error": ButtonColorVariant(
        name="error",
        fg_color=RGBColor(70, 10, 24),
        bg_color=RGBColor(240, 109, 128),
    ),
}

BUTTON_SIZES: dict[ButtonSize, ButtonSizeVariant] = {
    "icon": ButtonSizeVariant(name="icon", padding_x=0, padding_y=0),
    "small": ButtonSizeVariant(name="small", padding_x=2, padding_y=0),
    "medium": ButtonSizeVariant(name="medium", padding_x=4, padding_y=1),
    "large": ButtonSizeVariant(name="large", padding_x=6, padding_y=2),
}


class Button(Widget):
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
        """A simple button widget that can be clicked.

        Parameters
        ----------
        label : str
            The text displayed on the button.
        styles : tuple[str, ...]
            The styles applied to the button.
        disabled: bool = False
            Whether the button is disabled.
        padding: tuple[int, int, int, int] = (0, 0, 0, 0)
            Padding around the button content.
        on_click: Optional[Callable[[], None]] = None
            The callback function to be called when the button is clicked.
        state: ButtonState = "default"
            The state of the button.
        """
        super().__init__(name=kwargs.get("name", f"Button-{label}"), **kwargs)

        self.label = label
        self.padding = padding
        self.disabled = disabled
        self.on_click = on_click or (lambda: None)

        self.style, self.color, self.size = self._get_styles(style)
        self.state = state

        min_width, min_height = self.get_minimum_size()
        self.set_size(width=min_width, height=min_height)

    def _get_styles(
        self, style: str
    ) -> tuple[ButtonStyleVariant, ButtonColorVariant, ButtonSizeVariant]:
        """Get the button styles."""
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

    def get_minimum_size(self) -> tuple[int, int]:
        """Get the minimum size of the button."""
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
        """Render the button."""
        content: list[list[Char]] = draw_rectangle(
            self.region.width,
            self.region.height,
            border_style=self.style.border_style,
            border_color=self.color.bg_color,
            fill=Char(self.style.fill_char, self.color.bg_color, None),
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
                char.bg_color = self.color.bg_color.lighten(0.1)
            for char in content[-1]:
                char.char = depth_char_bottom
                char.fg_color = self.color.bg_color.darken(0.1)
                char.bg_color = self.color.bg_color

        text_fg = (
            self.color.fg_color
            if self.style.name == "solid" or self.style.name == "soft"
            else self.color.bg_color
        )

        text_bg = (
            self.color.bg_color
            if self.style.name == "solid" or self.style.name == "soft"
            else self.color.fg_color
        )

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
        """Simulate a button click."""
        if self.disabled:
            return
        self.on_click()
