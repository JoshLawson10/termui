from enum import Enum
from typing import Optional


class Color(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97


class Style(Enum):
    RESET = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    HIDDEN = 8


def colorize(
    text: str,
    fg: Optional[Color] = None,
    bg: Optional[Color] = None,
    style: Optional[Style] = None,
) -> str:
    codes: list[str] = []
    if fg:
        codes.append(str(fg.value))
    if bg:
        codes.append(str(bg.value + 10))
    if style:
        codes.append(str(style.value))

    if not codes:
        return text

    return f"\033[{';'.join(codes)}m{text}\033[0m"
