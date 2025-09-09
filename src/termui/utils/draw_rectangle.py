from enum import Enum
from typing import Literal, Optional

from termui.char import Char
from termui.color import Color
from termui.errors import DimensionError
from termui.utils.align import HorizontalAlignment, get_aligned_start_x


class BorderStyleChars(Enum):
    """Enum for border styles.

    Each style is represented by a tuple of characters for the corners, edges, and fill.

    Format:
    (top-left, top-right, bottom-left, bottom-right, left-vertical, right-vertical, top-horizontal, bottom-horizontal)
    """

    ASCII = ("+", "+", "+", "+", "|", "|", "-", "-")
    NONE = (" ", " ", " ", " ", " ", " ", " ", " ")
    ROUND = ("╭", "╮", "╰", "╯", "│", "│", "─", "─")
    SOLID = ("┌", "┐", "└", "┘", "│", "│", "─", "─")
    DOUBLE = ("╔", "╗", "╚", "╝", "║", "║", "═", "═")
    DASHED = ("┏", "┓", "┗", "┛", "╏", "╏", "╍", "╍")
    HEAVY = ("┏", "┓", "┗", "┛", "┃", "┃", "━", "━")
    FULL = ("█", "█", "█", "█", "█", "█", "█", "█")


BorderStyle = Literal[
    "ascii", "none", "round", "solid", "double", "dashed", "heavy", "full"
]
"""The character style to use for the border"""


def draw_rectangle(
    width: int,
    height: int,
    border_style: BorderStyle = "solid",
    border_color: Color = Color(255, 255, 255),
    title_color: Color = Color(255, 255, 255),
    title: Optional[str] = None,
    title_alignment: HorizontalAlignment = "left",
    fill: str | Char = " ",
) -> list[list[Char]]:
    """Draw a rectangle with the specified width, height, and border style.

    Args:
        width: The width of the rectangle.
        height: The height of the rectangle.
        border_style: The style of the border (default: "solid").
        border_color: The color of the border (default: white).
        title_color: The color of the title text (default: white).
        title: The title text to display (default: None).
        title_alignment: The alignment of the title text (default: "left").
        fill: The character or Char object to use for filling the rectangle (default: " ").
    """
    if width < 2 or height < 2:
        raise DimensionError("Width and height must be at least 2.")

    tl, tr, bl, br, lv, rv, th, bh = BorderStyleChars[border_style.upper()].value
    fill_char = Char(fill, None, None) if isinstance(fill, str) else fill

    rectangle: list[list[Char]] = []

    top_line = (
        [Char(tl, border_color)]
        + [Char(th, border_color)] * (width - 2)
        + [Char(tr, border_color)]
    )
    if title:
        title_text = f" {title} "
        start_x = get_aligned_start_x(title_text, width - 2, title_alignment)

        for i, char in enumerate(title_text):
            top_line[start_x + i + 1] = Char(char, title_color)
    rectangle.append(top_line)

    for _ in range(height - 2):
        rectangle.append(
            [Char(lv, border_color)]
            + [fill_char] * (width - 2)
            + [Char(rv, border_color)]
        )

    rectangle.append(
        [Char(bl, border_color)]
        + [Char(bh, border_color)] * (width - 2)
        + [Char(br, border_color)]
    )

    return rectangle
