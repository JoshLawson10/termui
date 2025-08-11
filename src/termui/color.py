from dataclasses import dataclass
from typing import Optional


@dataclass
class Color:
    """A class to represent a color."""

    r: int
    g: int
    b: int
    a: int = 255

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    @property
    def inverse(self) -> "Color":
        """Get the inverse color."""
        return Color(r=255 - self.r, g=255 - self.g, b=255 - self.b, a=self.a)

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Convert the color to an RGB tuple."""
        return (self.r, self.g, self.b)

    @property
    def rgba(self) -> tuple[int, int, int, int]:
        """Convert the color to an RGBA tuple."""
        return (self.r, self.g, self.b, self.a)

    @property
    def monochrome(self) -> "Color":
        """Convert the color to a monochrome (grayscale) color."""
        gray = round(self.r * 0.2126 + self.g * 0.7152 + self.b * 0.0722)
        return Color(gray, gray, gray, self.a)

    def lighten(self, percent: float) -> "Color":
        """Lighten the color by a percentage."""
        if not (0 <= percent <= 1):
            raise ValueError("Percent must be between 0 and 1.")
        factor = 1 + percent
        return Color(
            r=min(255, int(self.r * factor)),
            g=min(255, int(self.g * factor)),
            b=min(255, int(self.b * factor)),
            a=self.a,
        )

    def darken(self, percent: float) -> "Color":
        """Darken the color by a percentage."""
        if not (0 <= percent <= 1):
            raise ValueError("Percent must be between 0 and 1.")
        factor = 1 - percent
        return Color(
            r=max(0, int(self.r * factor)),
            g=max(0, int(self.g * factor)),
            b=max(0, int(self.b * factor)),
            a=self.a,
        )


def colorize(
    text: str,
    fg: Optional[Color] = None,
    bg: Optional[Color] = None,
) -> str:
    """Colorize text with ANSI escape codes."""
    if fg is None and bg is None:
        return text

    codes: list[str] = []

    if fg is not None:
        codes.append(f"38;2;{fg.r};{fg.g};{fg.b}")

    if bg is not None:
        codes.append(f"48;2;{bg.r};{bg.g};{bg.b}")

    return f"\033[{';'.join(codes)}m{text}\033[0m"
