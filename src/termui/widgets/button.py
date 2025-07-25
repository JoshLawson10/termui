from typing import Literal
from dataclasses import dataclass

from termui.widgets._widget import Widget
from termui.types.char import Char
from termui.colors import AnsiColor, RGBColor
from termui.utils.draw_rectangle import BorderStyle, draw_rectangle
from termui.utils.align import get_aligned_start_x, get_aligned_start_y


@dataclass
class ButtonVariant:
    name: str
    fg_color: AnsiColor | RGBColor
    bg_color: AnsiColor | RGBColor
    border_style: BorderStyle
    style: Literal["solid", "outline"] = "solid"


BUTTON_VARIANTS = {
    "default": ButtonVariant("default", AnsiColor.BLACK, AnsiColor.BLUE, "solid"),
    "primary": ButtonVariant("primary", AnsiColor.BLACK, AnsiColor.GREEN, "solid"),
    "success": ButtonVariant("success", AnsiColor.BLACK, AnsiColor.GREEN, "solid"),
    "warning": ButtonVariant("warning", AnsiColor.BLACK, AnsiColor.YELLOW, "solid"),
    "error": ButtonVariant("error", AnsiColor.BLACK, AnsiColor.RED, "solid"),
}


class Button(Widget):
    """A clickable button widget."""

    def __init__(self, text: str, **kwargs) -> None:
        self.text = text
        self.variant = BUTTON_VARIANTS.get(
            kwargs.get("variant", "default"), BUTTON_VARIANTS["default"]
        )
        self.style = kwargs.get("style", self.variant.style)
        self.on_click = kwargs.get("on_click", lambda: None)
        self.disabled = kwargs.get("disabled", False)
        self.padding = kwargs.get("padding", (0, 1, 0, 1))  # top, right, bottom, left

        min_width = len(text) + self.padding[1] + self.padding[3] + 2
        min_height = 3 + self.padding[0] + self.padding[2]

        kwargs.setdefault("width", max(min_width, kwargs.get("width", min_width)))
        kwargs.setdefault("height", max(min_height, kwargs.get("height", min_height)))

        super().__init__(**kwargs)

        self._state: Literal["default", "hover", "pressed"] = "default"

    def set_text(self, text: str) -> None:
        """Update the button text."""
        if text != self.text:
            self.text = text
            self.mark_dirty()

    def set_variant(self, variant: str) -> None:
        """Change the button variant."""
        if variant in BUTTON_VARIANTS:
            self.variant = BUTTON_VARIANTS[variant]
            self.mark_dirty()

    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable the button."""
        if disabled != self.disabled:
            self.disabled = disabled
            self.mark_dirty()

    def click(self) -> None:
        """Trigger the button click."""
        if not self.disabled and callable(self.on_click):
            self.on_click()

    def render(self) -> list[list[Char]]:
        """Render the button."""
        if self.style == "solid":
            fg = self.variant.fg_color
            bg = self.variant.bg_color
            border_color = self.variant.bg_color
            border_style = "full"
            fill = Char("█", self.variant.bg_color, None)
        else:
            fg = self.variant.bg_color
            bg = None
            border_color = self.variant.bg_color
            border_style = self.variant.border_style
            fill = Char(" ", fg, bg)

        # Apply disabled styling
        if self.disabled:
            fg = AnsiColor.BRIGHT_BLACK
            bg = AnsiColor.BLACK if self.style == "solid" else None
            border_color = AnsiColor.BRIGHT_BLACK

        content = draw_rectangle(
            self.width,
            self.height,
            border_style=border_style,
            border_color=border_color,
            fill=fill,
        )

        # Render text
        text_line = [Char(c, fg, bg) for c in self.text]
        text_start_x = get_aligned_start_x(self.text, self.width - 2, "center") + 1
        text_start_y = get_aligned_start_y(self.height, "middle")

        # Place text in the button
        if (
            0 <= text_start_y < len(content)
            and text_start_x + len(text_line) <= self.width
        ):
            for i, char in enumerate(text_line):
                if text_start_x + i < len(content[text_start_y]):
                    content[text_start_y][text_start_x + i] = char

        return content
