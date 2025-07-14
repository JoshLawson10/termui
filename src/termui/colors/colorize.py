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

    codes: list[str] = []

    if fg is not None:
        if isinstance(fg, AnsiColor):
            codes.append(str(fg.value))
        elif isinstance(fg, RGBColor):
            codes.append(f"38;2;{fg.red};{fg.green};{fg.blue}")

    if bg is not None:
        if isinstance(bg, AnsiColor):
            codes.append(str(bg.value + 10))
        elif isinstance(bg, RGBColor):
            codes.append(f"48;2;{bg.red};{bg.green};{bg.blue}")

    return f"\033[{';'.join(codes)}m{text}\033[0m"
