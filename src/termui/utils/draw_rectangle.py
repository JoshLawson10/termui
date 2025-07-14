from enum import Enum
from typing import Optional, Literal

from termui.colors.rgb import RGBColor
from termui.colors.ansi import AnsiColor
from termui.types.char import Char
from termui.utils.align import HorizontalAlignment, get_aligned_start_x


class BorderStyleChars(Enum):
    """Enum for border styles.

    Each style is represented by a tuple of characters for the corners, edges, and fill.

    Format:
    (top-left, top-right, bottom-left, bottom-right, left-vertical, right-vertical, top-horizontal, bottom-horizontal)
    """

    ASCII = ("+", "+", "+", "+", "-", "-", "|", "|")
    NONE = (" ", " ", " ", " ", " ", " ", " ", " ")
    ROUND = ("╭", "╮", "╰", "╯", "│", "│", "─", "─")
    SOLID = ("┌", "┐", "└", "┘", "│", "│", "─", "─")
    DOUBLE = ("╔", "╗", "╚", "╝", "║", "═", "═", "═")
    DASHED = ("┏", "┓", "┗", "┛", "╏", "╍", "╍", "╍")
    HEAVY = ("┏", "┓", "┗", "┛", "┃", "━", "━", "━")
    FULL = ("█", "█", "█", "█", "█", "█", "█", "█")


type BorderStyle = Literal[
    "ascii", "none", "round", "solid", "double", "dashed", "heavy", "full"
]


def draw_rectangle(
    width: int,
    height: int,
    border_style: BorderStyle = "solid",
    border_color: AnsiColor | RGBColor = AnsiColor.WHITE,
    title_color: AnsiColor | RGBColor = AnsiColor.WHITE,
    title: Optional[str] = None,
    title_alignment: HorizontalAlignment = "left",
    fill: str | Char = " ",
) -> list[list[Char]]:
    """Draw a rectangle with the specified width, height, and border style."""
    if width < 2 or height < 2:
        raise ValueError("Width and height must be at least 2.")

    tl, tr, bl, br, lv, rv, th, bh = BorderStyleChars[border_style.upper()].value
    tl_char = Char(tl, border_color)
    tr_char = Char(tr, border_color)
    bl_char = Char(bl, border_color)
    br_char = Char(br, border_color)
    lv_char = Char(lv, border_color)
    rv_char = Char(rv, border_color)
    th_char = Char(th, border_color)
    bh_char = Char(bh, border_color)
    fill_char = Char(fill, None, None) if isinstance(fill, str) else fill

    rectangle: list[list[Char]] = []

    top_line = [tl_char] + [th_char] * (width - 2) + [tr_char]
    if title:
        title_text = f" {title} "
        start_x = get_aligned_start_x(title_text, width - 2, title_alignment)

        for i, char in enumerate(title_text):
            top_line[start_x + i + 1] = Char(char, title_color)
    rectangle.append(top_line)

    for _ in range(height - 2):
        rectangle.append([lv_char] + [fill_char] * (width - 2) + [rv_char])

    rectangle.append([bl_char] + [bh_char] * (width - 2) + [br_char])

    return rectangle
