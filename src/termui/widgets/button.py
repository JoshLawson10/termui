from typing import Callable, Literal
from dataclasses import dataclass
from enum import Enum, auto

from termui.widgets._widget import Widget
from termui.types.char import Char
from termui.colors.ansi import AnsiColor


type ButtonStyle = Literal["solid", "outline", "text"]


class BorderStyle(Enum):
    """Enum for border styles."""

    ASCII = ("+", "+", "+", "+", "-", "|")
    NONE = (" ", " ", " ", " ", " ", " ")
    ROUND = ("╭", "╮", "╰", "╯", "│", "─")
    SOLID = ("┌", "┐", "└", "┘", "│", "─")
    DOUBLE = ("╔", "╗", "╚", "╝", "║", "═")
    DASHED = ("┏", "┓", "┗", "┛", "╏", "╍")
    HEAVY = ("┏", "┓", "┗", "┛", "┃", "━")
    THICK = ("█", "█", "█", "█", "█", "▀")


@dataclass
class ButtonVariant:
    name: str
    fg_color: AnsiColor
    bg_color: AnsiColor
    border_style: BorderStyle
    style: ButtonStyle = "solid"


BUTTON_VARIANTS: dict[str, ButtonVariant] = {
    "default": ButtonVariant(
        name="default",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.BLUE,
        border_style=BorderStyle.SOLID,
        style="solid",
    ),
    "primary": ButtonVariant(
        name="primary",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.GREEN,
        border_style=BorderStyle.SOLID,
        style="solid",
    ),
    "success": ButtonVariant(
        name="success",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.GREEN,
        border_style=BorderStyle.SOLID,
        style="solid",
    ),
    "warning": ButtonVariant(
        name="warning",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.YELLOW,
        border_style=BorderStyle.SOLID,
        style="solid",
    ),
    "error": ButtonVariant(
        name="error",
        fg_color=AnsiColor.BLACK,
        bg_color=AnsiColor.RED,
        border_style=BorderStyle.SOLID,
        style="solid",
    ),
}


class Button(Widget):
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

    def __init__(
        self,
        label: str,
        *,
        name: str | None = None,
        variant: str = "default",
        style: ButtonStyle = "solid",
        on_click: Callable,
        disabled: bool = False,
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
    ) -> None:
        """Initialize a Button widget."""
        super().__init__(
            name=name if name else f"Button {label}",
        )
        if not callable(on_click):
            raise TypeError("on_click must be a callable function.")
        self.name = name if name else f"Button {label}"
        self.variant = BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS["default"])
        self.style = style
        self.variant.style = style
        self.label = label
        self.width = len(label) + padding[1] + padding[3] + 2
        self.height = 3 + padding[0] + padding[2]
        self.on_click = on_click
        self.disabled = disabled
        self.padding = padding

        self._state: Literal["default", "selected", "pressed"] = "default"

    def render(self) -> list[list[Char]]:
        """Render the button."""
        self.width = len(self.label) + self.padding[1] + self.padding[3] + 2
        self.height = 3 + self.padding[0] + self.padding[2]

        tl, tr, bl, br, v, h = self.variant.border_style.value

        if self.variant.style == "solid":
            tl = "█"
            tr = "█"
            bl = "█"
            br = "█"
            v = "█"
            h = "█"
            fg = self.variant.fg_color
            bg = self.variant.bg_color
            border_color = bg
            empty_char = Char("█", bg, bg)
        else:
            fg = self.variant.bg_color
            bg = None
            border_color = self.variant.bg_color
            empty_char = Char(" ", fg, bg)
        tl = Char(tl, border_color, None)
        tr = Char(tr, border_color, None)
        bl = Char(bl, border_color, None)
        br = Char(br, border_color, None)
        v = Char(v, border_color, None)
        h = Char(h, border_color, None)
        content: list[list[Char]] = [[tl] + [h] * (self.width - 2) + [tr]]

        for _ in range(self.padding[0]):
            content.append([empty_char] * self.width)

        label_line: list[Char] = (
            [empty_char] * self.padding[3]
            + [Char(c, fg, bg) for c in self.label]
            + [empty_char] * (self.width - len(self.label) - self.padding[3] - 2)
        )
        content.append([v] + label_line + [v])

        for _ in range(self.padding[2]):
            content.append([empty_char] * self.width)

        content.append([bl] + [h] * (self.width - 2) + [br])

        return content

    def click(self) -> None:
        """Simulate a button click."""
        if self.disabled:
            return
        self.on_click()

    """A widget that represents a button."""
