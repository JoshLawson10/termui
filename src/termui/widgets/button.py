from dataclasses import dataclass
from typing import Literal

from termui.colors import AnsiColor, RGBColor
from termui.types.char import Char
from termui.utils.align import get_aligned_start_x, get_aligned_start_y
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle

from termui.widgets._widget import Widget


type ButtonStyle = Literal["solid", "outline"]


@dataclass
class ButtonVariant:
    name: str
    fg_color: AnsiColor | RGBColor
    bg_color: AnsiColor | RGBColor
    border_style: BorderStyle
    style: ButtonStyle = "solid"


BUTTON_VARIANTS: dict[str, ButtonVariant] = {
    "default": ButtonVariant(
        name="default",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.BLUE,
        border_style="solid",
        style="solid",
    ),
    "primary": ButtonVariant(
        name="primary",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.GREEN,
        border_style="solid",
        style="solid",
    ),
    "success": ButtonVariant(
        name="success",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.GREEN,
        border_style="solid",
        style="solid",
    ),
    "warning": ButtonVariant(
        name="warning",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.YELLOW,
        border_style="solid",
        style="solid",
    ),
    "error": ButtonVariant(
        name="error",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.RED,
        border_style="solid",
        style="solid",
    ),
}


class Button(Widget):
    def __init__(self, label: str, **kwargs) -> None:
        """A simple button widget that can be clicked.

        Parameters
        ----------
        label : str
            The text displayed on the button.
        variant : ButtonVariant, optional
            The visual style of the button, by default "default".
        style : ButtonStyle, optional
            The button style, by default "solid".
        name : str, optional
            The name of the button, by default None.
        on_click : Callable[[str], None]
            The callback function to be called when the button is clicked.
        disabled : bool, optional
            Whether the button is disabled, by default False.
        padding : tuple[int, int, int, int], optional
            Padding around the button content, by default (0, 0, 0, 0).
        """
        super().__init__(name=kwargs.get("name", f"Button {label}"))
        self.variant = BUTTON_VARIANTS.get(
            kwargs.get("variant", "default"), BUTTON_VARIANTS["default"]
        )
        self.style = kwargs.get("style", self.variant.style)
        self.variant.style = self.style
        self.label = label

        self.on_click = kwargs.get("on_click", lambda: None)
        if not callable(self.on_click):
            raise TypeError("on_click must be a callable function.")

        self.disabled = kwargs.get("disabled", False)
        self.padding = kwargs.get("padding", (0, 0, 0, 0))

        min_width = len(label) + self.padding[1] + self.padding[3] + 2
        min_height = 3 + self.padding[0] + self.padding[2]

        self.set_size(
            width=max(min_width, kwargs.get("width", min_width)),
            height=max(min_height, kwargs.get("height", min_height)),
        )

        self._state: Literal["default", "selected", "pressed"] = "default"

    def render(self) -> list[list[Char]]:
        """Render the button."""

        if self.style == "solid":
            fg = self.variant.fg_color
            bg = self.variant.bg_color
            border_color = self.variant.bg_color
            border_style = "full"
            fill = Char("█", self.variant.bg_color, None)
        else:
            fg = self.variant.bg_color
            bg = None
            border_color = self.variant.bg_color
            border_style = self.variant.border_style
            fill = Char(" ", fg, bg)

        content: list[list[Char]] = draw_rectangle(
            self.region.width,
            self.region.height,
            border_style=border_style,
            border_color=border_color,
            fill=fill,
        )

        text_line: list[Char] = [Char(c, fg, bg) for c in self.label]

        text_start_x = get_aligned_start_x(
            self.label, self.region.width - self.padding[1] - self.padding[3], "center"
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
