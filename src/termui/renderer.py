from dataclasses import dataclass
import sys

from termui.widgets.widget import Widget
from termui.geometry import Region
from termui.render_geometry import RenderedObject
from termui.utils import move_cursor_to, get_terminal_size, clear_terminal


class Renderer:
    def __init__(self) -> None:
        self.widgets: list[RenderedObject] = []
        self.screen_width, self.screen_height = get_terminal_size()
        self.previous_frame: list[list[str]] = [
            [" "] * self.screen_width for _ in range(self.screen_height)
        ]
        self.current_frame: list[list[str]] = [
            [" "] * self.screen_width for _ in range(self.screen_height)
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
            row[:] = [" "] * self.screen_width

        screen_changed: bool = False
        self.widgets.sort(key=lambda obj: obj.index)
        for rendered_object in self.widgets:
            if not rendered_object.dirty:
                continue

            widget: Widget = rendered_object.widget
            region: Region = rendered_object.region

            widget_content: list[list[str]] = widget.render()
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
                sys.stdout.write(new_char)
                screen_changed = True

        if screen_changed:
            sys.stdout.flush()
        self.previous_frame = [row[:] for row in self.current_frame]
