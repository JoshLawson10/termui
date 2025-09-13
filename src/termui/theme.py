from dataclasses import dataclass, field
from functools import cached_property
from typing import Literal, Optional

from termui.color import Color

PrimitiveColors = Literal[
    "primary", "secondary", "accent", "info", "success", "warning", "error"
]


@dataclass
class Theme:
    """Defines a theme for the application.

    Attributes:
        name: The name of the theme.
        dark: If the theme is a dark theme.
        primary: Primary color
        primary_content: Foreground content color to use on `primary` color
        secondary: Optional secondary color
        secondary_content: Foreground content color to use on `secondary` color
        accent: Optional accent colour
        accent_content: Foreground content color to use on `accent` color
        neutral: Neutral dark color, for not-saturated parts of UI
        neutral_content: Foreground content color to use on `neutral` color
        base_100: Base surface color of page, used for blank backgrounds
        base_200: Base color, darker shade, to create elevations
        base_300: Base color, even darker shade, to create elevations
        base_content: Foreground content color to use on `base` color
        info: Info color, for informative/helpful messages
        info_content: Foreground content color to use on `info` color
        success: Success color, for success/safe messages
        success_content: Foreground content color to use on `success` color
        warning: Warning color, for warning/caution messages
        warning_content: Foreground content color to use on `warning` color
        error: Error color, for error/danger/destructive messages
        error_content: Foreground content color to use on `error` color
    """

    name: str
    """The name of the theme.

    Once a theme is registered to the app instance (`App.register_theme`), it can then
    be set with `App.theme = theme_name`.
    """
    dark: bool
    """Whether the theme is dark or not."""

    primary: Color
    primary_content: Optional[Color] = field(default=None)
    secondary: Optional[Color] = field(default=None)
    secondary_content: Optional[Color] = field(default=None)
    accent: Optional[Color] = field(default=None)
    accent_content: Optional[Color] = field(default=None)
    neutral: Optional[Color] = field(default=None)
    neutral_content: Optional[Color] = field(default=None)
    base_100: Optional[Color] = field(default=None)
    base_200: Optional[Color] = field(default=None)
    base_300: Optional[Color] = field(default=None)
    base_content: Optional[Color] = field(default=None)
    info: Optional[Color] = field(default=None)
    info_content: Optional[Color] = field(default=None)
    success: Optional[Color] = field(default=None)
    success_content: Optional[Color] = field(default=None)
    warning: Optional[Color] = field(default=None)
    warning_content: Optional[Color] = field(default=None)
    error: Optional[Color] = field(default=None)
    error_content: Optional[Color] = field(default=None)

    @cached_property
    def create(self) -> dict[str, Color]:
        """Create a mapping of colours to their names.

        Returns:
            A mapping of colours to their names.
        """

        primary = self.primary
        primary_content = self.primary_content or primary.content_color
        secondary = self.secondary or primary
        secondary_content = self.secondary_content or secondary.content_color
        accent = self.accent or secondary
        accent_content = self.accent_content or accent.content_color
        neutral = self.neutral or secondary
        neutral_content = self.neutral_content or neutral.content_color
        base_100 = self.base_100 or primary
        base_200 = self.base_200 or secondary
        base_300 = self.base_300 or accent
        base_content = self.base_content or base_100.content_color
        info = self.info or primary
        info_content = self.info_content or primary.content_color
        success = self.success or primary
        success_content = self.success_content or primary.content_color
        warning = self.warning or primary
        warning_content = self.warning_content or primary.content_color
        error = self.error or secondary
        error_content = self.error_content or primary.content_color

        colors: dict[str, Color] = {
            # Base Colors
            "primary": primary,
            "secondary": secondary,
            "accent": accent,
            "neutral": neutral,
            "base_100": base_100,
            "base_200": base_200,
            "base_300": base_300,
            "info": info,
            "success": success,
            "warning": warning,
            "error": error,
            # Content Colors
            "primary_content": primary_content,
            "secondary_content": secondary_content,
            "accent_content": accent_content,
            "neutral_content": neutral_content,
            "base_content": base_content,
            "info_content": info_content,
            "success_content": success_content,
            "warning_content": warning_content,
            "error_content": error_content,
        }

        return colors

    def get(self, color_name: str) -> Color | None:
        """Get the theme color by its name.

        Args:
            color_name: The name of the theme color.
        """

        return self.create.get(color_name)

    def __getitem__(self, color_name: str) -> Color:
        """Get the theme color by its name using bracket notation.

        Args:
            color_name: The name of the theme color.

        Returns:
            The color.

        Raises:
            KeyError: If the color name is not found.
        """
        color = self.get(color_name)
        if color is None:
            raise KeyError(f"Color '{color_name}' not found in theme '{self.name}'")
        return color


# Dark Theme: https://github.com/saadeghi/daisyui/blob/master/packages/daisyui/src/themes/dark.css
dark_theme = Theme(
    name="dark",
    dark=True,
    primary=Color(94, 100, 224),
    primary_content=Color(238, 240, 255),
    secondary=Color(217, 95, 187),
    secondary_content=Color(237, 228, 240),
    accent=Color(100, 213, 198),
    accent_content=Color(67, 105, 103),
    neutral=Color(28, 31, 48),
    neutral_content=Color(227, 230, 240),
    base_100=Color(55, 58, 79),
    base_200=Color(50, 53, 72),
    base_300=Color(46, 48, 66),
    base_content=Color(247, 248, 253),
    info=Color(118, 176, 245),
    info_content=Color(50, 73, 108),
    success=Color(106, 218, 155),
    success_content=Color(61, 107, 81),
    warning=Color(239, 210, 99),
    warning_content=Color(128, 97, 56),
    error=Color(235, 119, 101),
    error_content=Color(87, 52, 49),
)

# Light Theme: https://github.com/saadeghi/daisyui/blob/master/packages/daisyui/src/themes/light.css
light_theme = Theme(
    name="light",
    dark=False,
    primary=Color(61, 56, 184),
    primary_content=Color(227, 230, 252),
    secondary=Color(217, 95, 187),
    secondary_content=Color(237, 228, 240),
    accent=Color(100, 213, 198),
    accent_content=Color(67, 105, 103),
    neutral=Color(28, 31, 48),
    neutral_content=Color(227, 230, 240),
    base_100=Color(255, 255, 255),
    base_200=Color(250, 250, 250),
    base_300=Color(242, 242, 242),
    base_content=Color(46, 48, 58),
    info=Color(118, 176, 245),
    info_content=Color(50, 73, 108),
    success=Color(106, 218, 155),
    success_content=Color(61, 107, 81),
    warning=Color(239, 210, 99),
    warning_content=Color(128, 97, 56),
    error=Color(235, 119, 101),
    error_content=Color(87, 52, 49),
)

# One Dark Theme: https://github.com/Binaryify/OneDark-Pro
one_dark_theme = Theme(
    name="one_dark",
    dark=True,
    primary=Color(97, 175, 239),
    primary_content=Color(40, 44, 52),
    secondary=Color(198, 120, 221),
    secondary_content=Color(40, 44, 52),
    accent=Color(86, 182, 194),
    accent_content=Color(40, 44, 52),
    neutral=Color(33, 37, 43),
    neutral_content=Color(171, 178, 191),
    base_100=Color(40, 44, 52),
    base_200=Color(33, 37, 43),
    base_300=Color(26, 29, 36),
    base_content=Color(171, 178, 191),
    info=Color(97, 175, 239),
    info_content=Color(40, 44, 52),
    success=Color(152, 195, 121),
    success_content=Color(40, 44, 52),
    warning=Color(229, 192, 123),
    warning_content=Color(40, 44, 52),
    error=Color(224, 108, 117),
    error_content=Color(40, 44, 52),
)

# Catppuccin Latte Theme (Light): https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md
catppuccin_latte_theme = Theme(
    name="catppuccin_latte",
    dark=False,
    primary=Color(30, 102, 245),
    primary_content=Color(239, 241, 245),
    secondary=Color(136, 57, 239),
    secondary_content=Color(239, 241, 245),
    accent=Color(4, 165, 229),
    accent_content=Color(239, 241, 245),
    neutral=Color(204, 208, 218),
    neutral_content=Color(76, 79, 105),
    base_100=Color(239, 241, 245),
    base_200=Color(230, 233, 239),
    base_300=Color(220, 224, 232),
    base_content=Color(76, 79, 105),
    info=Color(30, 102, 245),
    info_content=Color(239, 241, 245),
    success=Color(64, 160, 43),
    success_content=Color(239, 241, 245),
    warning=Color(223, 142, 29),
    warning_content=Color(239, 241, 245),
    error=Color(210, 15, 57),
    error_content=Color(239, 241, 245),
)

# Catppuccin Mocha Theme: https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md
catppuccin_mocha_theme = Theme(
    name="catppuccin_mocha",
    dark=True,
    primary=Color(137, 180, 250),
    primary_content=Color(30, 30, 46),
    secondary=Color(203, 166, 247),
    secondary_content=Color(30, 30, 46),
    accent=Color(116, 199, 236),
    accent_content=Color(30, 30, 46),
    neutral=Color(49, 50, 68),
    neutral_content=Color(205, 214, 244),
    base_100=Color(30, 30, 46),
    base_200=Color(24, 24, 37),
    base_300=Color(17, 17, 27),
    base_content=Color(205, 214, 244),
    info=Color(137, 180, 250),
    info_content=Color(30, 30, 46),
    success=Color(166, 227, 161),
    success_content=Color(30, 30, 46),
    warning=Color(249, 226, 175),
    warning_content=Color(30, 30, 46),
    error=Color(243, 139, 168),
    error_content=Color(30, 30, 46),
)

# Dracula Theme: https://github.com/dracula/template/blob/main/sample/Dracula.yml
dracula_theme = Theme(
    name="dracula",
    dark=True,
    primary=Color(139, 233, 253),  # Cyan
    primary_content=Color(40, 42, 54),  # Background
    secondary=Color(255, 121, 198),  # Pink
    secondary_content=Color(40, 42, 54),
    accent=Color(189, 147, 249),  # Purple
    accent_content=Color(40, 42, 54),
    neutral=Color(68, 71, 90),  # Current line
    neutral_content=Color(248, 248, 242),  # Foreground
    base_100=Color(40, 42, 54),  # Background
    base_200=Color(68, 71, 90),  # Current line
    base_300=Color(98, 114, 164),  # Comment
    base_content=Color(248, 248, 242),  # Foreground
    info=Color(139, 233, 253),  # Cyan
    info_content=Color(40, 42, 54),
    success=Color(80, 250, 123),  # Green
    success_content=Color(40, 42, 54),
    warning=Color(241, 250, 140),  # Yellow
    warning_content=Color(40, 42, 54),
    error=Color(255, 85, 85),  # Red
    error_content=Color(40, 42, 54),
)

# Tokyo Night Theme: https://github.com/tokyo-night/tokyo-night-vscode-theme
tokyo_night_theme = Theme(
    name="tokyo_night",
    dark=True,
    primary=Color(125, 207, 255),  # Blue
    primary_content=Color(26, 27, 38),  # Background
    secondary=Color(187, 154, 247),  # Purple
    secondary_content=Color(26, 27, 38),
    accent=Color(115, 218, 202),  # Teal
    accent_content=Color(26, 27, 38),
    neutral=Color(55, 56, 70),  # Darker gray
    neutral_content=Color(169, 177, 214),  # Foreground
    base_100=Color(26, 27, 38),  # Background
    base_200=Color(22, 22, 30),  # Darker
    base_300=Color(18, 18, 25),  # Even darker
    base_content=Color(169, 177, 214),  # Foreground
    info=Color(125, 207, 255),  # Blue
    info_content=Color(26, 27, 38),
    success=Color(158, 206, 106),  # Green
    success_content=Color(26, 27, 38),
    warning=Color(224, 175, 104),  # Orange
    warning_content=Color(26, 27, 38),
    error=Color(247, 118, 142),  # Red
    error_content=Color(26, 27, 38),
)

# Monokai Theme
monokai_theme = Theme(
    name="monokai",
    dark=True,
    primary=Color(102, 217, 239),  # Cyan
    primary_content=Color(39, 40, 34),  # Background
    secondary=Color(174, 129, 255),  # Purple
    secondary_content=Color(39, 40, 34),
    accent=Color(255, 216, 102),  # Yellow
    accent_content=Color(39, 40, 34),
    neutral=Color(73, 72, 62),  # Dark gray
    neutral_content=Color(248, 248, 242),  # Foreground
    base_100=Color(39, 40, 34),  # Background
    base_200=Color(73, 72, 62),  # Selection
    base_300=Color(117, 113, 94),  # Comment
    base_content=Color(248, 248, 242),  # Foreground
    info=Color(102, 217, 239),  # Cyan
    info_content=Color(39, 40, 34),
    success=Color(166, 226, 46),  # Green
    success_content=Color(39, 40, 34),
    warning=Color(255, 216, 102),  # Yellow
    warning_content=Color(39, 40, 34),
    error=Color(249, 38, 114),  # Pink/Red
    error_content=Color(39, 40, 34),
)


DEFAULT_THEMES: dict[str, Theme] = {
    "dark": dark_theme,
    "light": light_theme,
    "one-dark": one_dark_theme,
    "catppuccin-latte": catppuccin_latte_theme,
    "catppuccin-mocha": catppuccin_mocha_theme,
    "dracula": dracula_theme,
    "tokyo-night": tokyo_night_theme,
    "monokai": monokai_theme,
}
