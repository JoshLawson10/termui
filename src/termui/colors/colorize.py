from typing import Optional
from termui.colors.ansi import AnsiColor
from termui.colors.rgb import RGBColor


def colorize(
    text: str,
    fg: Optional[AnsiColor | RGBColor] = None,
    bg: Optional[AnsiColor | RGBColor] = None,
) -> str:
    """Colorize text with ANSI escape codes."""
    if fg is None and bg is None:
        return text

    codes: str = ""
    if isinstance(fg, AnsiColor):
        codes += str(fg.value)
    elif isinstance(fg, RGBColor):
        codes += f"38;2;{fg.red};{fg.green};{fg.blue}"

    if isinstance(bg, AnsiColor):
        codes += str(bg.value + 10)
    elif isinstance(bg, RGBColor):
        codes += f";48;2;{bg.red};{bg.green};{bg.blue}"

    return f"\033[{codes}m{text}\033[0m"
