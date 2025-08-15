from dataclasses import dataclass
from typing import Optional


@dataclass
class Color:
    """A class to represent a color with RGBA values.

    Args:
        r: Red component (0-255).
        g: Green component (0-255).
        b: Blue component (0-255).
        a: Alpha component (0-255). Defaults to 255 (fully opaque).
    """

    r: int
    g: int
    b: int
    a: int = 255

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    @property
    def inverse(self) -> "Color":
        """Get the inverse color.

        Returns:
            A new Color instance with inverted RGB values (255 - component).
            Alpha value remains unchanged.
        """
        return Color(r=255 - self.r, g=255 - self.g, b=255 - self.b, a=self.a)

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Convert the color to an RGB tuple.

        Returns:
            A tuple containing (r, g, b) values.
        """
        return (self.r, self.g, self.b)

    @property
    def rgba(self) -> tuple[int, int, int, int]:
        """Convert the color to an RGBA tuple.

        Returns:
            A tuple containing (r, g, b, a) values.
        """
        return (self.r, self.g, self.b, self.a)

    @property
    def monochrome(self) -> "Color":
        """Convert the color to a monochrome (grayscale) color.

        Uses the standard luminance formula: 0.2126*R + 0.7152*G + 0.0722*B

        Returns:
            A new Color instance with grayscale values. Alpha remains unchanged.
        """
        gray = round(self.r * 0.2126 + self.g * 0.7152 + self.b * 0.0722)
        return Color(gray, gray, gray, self.a)

    def lighten(self, percent: float) -> "Color":
        """Lighten the color by a percentage.

        Args:
            percent: The percentage to lighten (0.0 to 1.0).

        Returns:
            A new Color instance with lightened RGB values. Values are
            clamped to a maximum of 255.

        Raises:
            ValueError: If percent is not between 0 and 1.
        """
        if not (0 <= percent <= 1):
            raise ValueError("Percent must be between 0 and 1.")
        return Color(
            r=min(255, int(self.r + self.r * percent)),
            g=min(255, int(self.g + self.g * percent)),
            b=min(255, int(self.b + self.b * percent)),
            a=self.a,
        )

    def darken(self, percent: float) -> "Color":
        """Darken the color by a percentage.

        Args:
            percent: The percentage to darken (0.0 to 1.0).

        Returns:
            A new Color instance with darkened RGB values. Values are
            clamped to a minimum of 0.

        Raises:
            ValueError: If percent is not between 0 and 1.
        """
        if not (0 <= percent <= 1):
            raise ValueError("Percent must be between 0 and 1.")
        return Color(
            r=max(0, int(self.r - self.r * percent)),
            g=max(0, int(self.g - self.g * percent)),
            b=max(0, int(self.b - self.b * percent)),
            a=self.a,
        )


def colorize(
    text: str,
    fg: Optional[Color] = None,
    bg: Optional[Color] = None,
) -> str:
    """Colorize text with ANSI escape codes.

    Args:
        text: The text to colorize.
        fg: The foreground color. If None, no foreground color is applied.
        bg: The background color. If None, no background color is applied.

    Returns:
        The text wrapped with appropriate ANSI escape codes for coloring.
        If both fg and bg are None, returns the original text unchanged.
    """
    if fg is None and bg is None:
        return text

    codes: list[str] = []

    if fg is not None:
        codes.append(f"38;2;{fg.r};{fg.g};{fg.b}")

    if bg is not None:
        codes.append(f"48;2;{bg.r};{bg.g};{bg.b}")

    return f"\033[{';'.join(codes)}m{text}\033[0m"
