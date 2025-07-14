from enum import Enum

from termui.colors.rgb import RGBColor
from termui.colors.ansi import AnsiColor
from termui.types.char import Char


class BorderStyle(Enum):
    """Enum for border styles."""

    ASCII = ("+", "+", "+", "+", "-", "|")
    NONE = (" ", " ", " ", " ", " ", " ")
    ROUND = ("╭", "╮", "╰", "╯", "│", "─")
    SOLID = ("┌", "┐", "└", "┘", "│", "─")
    DOUBLE = ("╔", "╗", "╚", "╝", "║", "═")
    DASHED = ("┏", "┓", "┗", "┛", "╏", "╍")
    HEAVY = ("┏", "┓", "┗", "┛", "┃", "━")
    FULL = ("█", "█", "█", "█", "█", "█")


def draw_rectangle(
    width: int,
    height: int,
    border_style: BorderStyle = BorderStyle.SOLID,
    border_color: AnsiColor | RGBColor = AnsiColor.WHITE,
    fill: str = " ",
) -> list[list[Char]]:
    """Draw a rectangle with the specified width, height, and border style."""
    if width < 2 or height < 2:
        raise ValueError("Width and height must be at least 2.")

    tl, tr, bl, br, v, h = border_style.value
    tl_char = Char(tl, border_color)
    tr_char = Char(tr, border_color)
    bl_char = Char(bl, border_color)
    br_char = Char(br, border_color)
    v_char = Char(v, border_color)
    h_char = Char(h, border_color)
    fill_char = Char(fill, None, None)

    rectangle: list[list[Char]] = []

    rectangle.append([tl_char] + [h_char] * (width - 2) + [tr_char])

    for _ in range(height - 2):
        rectangle.append([v_char] + [fill_char] * (width - 2) + [v_char])

    rectangle.append([bl_char] + [h_char] * (width - 2) + [br_char])

    return rectangle
