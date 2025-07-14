import sys

from termui.colors import colorize
from termui.widgets._widget import Widget
from termui.utils.geometry import Region
from termui.types.char import Char
from termui.types.render_types import RenderedObject
from termui.utils.terminal_utils import (
    move_cursor_to,
    get_terminal_size,
    clear_terminal,
)


class Renderer:
    def __init__(self) -> None:
        self.widgets: list[RenderedObject] = []
        self.screen_width, self.screen_height = get_terminal_size()
        self.previous_frame: list[list[Char]] = [
            [Char(" ") for _ in range(self.screen_width)]
            for _ in range(self.screen_height)
        ]
        self.current_frame: list[list[Char]] = [
            [Char(" ") for _ in range(self.screen_width)]
            for _ in range(self.screen_height)
        ]
        clear_terminal()

    def pipe(self, widget: Widget, x: int, y: int, index: int = 1) -> None:
        """Add a rendered object to the renderer."""
        region = Region(x, y, widget.width, widget.height)
        rendered_object = RenderedObject(widget=widget, region=region, index=index)
        self.widgets.append(rendered_object)

    def render(self) -> None:
        """Render all piped widgets to the terminal."""
        for row in self.current_frame:
            row[:] = [Char(" ")] * self.screen_width

        screen_changed: bool = False
        self.widgets.sort(key=lambda obj: obj.index)
        for rendered_object in self.widgets:
            if not rendered_object.dirty:
                continue

            widget: Widget = rendered_object.widget
            region: Region = rendered_object.region

            widget_content: list[list[Char]] = widget.render()
            for row_index, row in enumerate(widget_content):
                for col_index, char in enumerate(row):
                    if (
                        0 <= region.y + row_index < self.screen_height
                        and 0 <= region.x + col_index < self.screen_width
                    ):
                        self.current_frame[region.y + row_index][
                            region.x + col_index
                        ] = char

        for y, (old_char, new_char) in enumerate(
            zip(self.previous_frame, self.current_frame)
        ):
            for x, (old_char, new_char) in enumerate(zip(old_char, new_char)):
                if old_char == new_char:
                    continue
                move_cursor_to(x + 1, y + 1)
                sys.stdout.write(
                    colorize(new_char.char, fg=new_char.fg_color, bg=new_char.bg_color)
                )
                screen_changed = True

        if screen_changed:
            sys.stdout.flush()
        self.previous_frame = [row[:] for row in self.current_frame]
