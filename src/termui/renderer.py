import sys
import threading
from typing import List, Dict, Set, Optional

from termui.colors import colorize
from termui.widgets._widget import Widget
from termui.utils.geometry import Region
from termui.types.char import Char
from termui.types.render_types import RenderedObject
from termui.cursor import Cursor as cursor
from termui.utils.terminal_utils import (
    get_terminal_size,
    clear_terminal,
)


class Renderer:
    def __init__(self) -> None:
        self.widgets: List[RenderedObject] = []
        self._widget_lookup: Dict[Widget, RenderedObject] = {}
        self._lock = threading.Lock()

        self.screen_width, self.screen_height = get_terminal_size()
        self._initialize_frames()

        clear_terminal()
        cursor.hide()

    def _initialize_frames(self) -> None:
        """Initialize the frame buffers."""
        self.previous_frame: List[List[Char]] = [
            [Char(" ") for _ in range(self.screen_width)]
            for _ in range(self.screen_height)
        ]
        self.current_frame: List[List[Char]] = [
            [Char(" ") for _ in range(self.screen_width)]
            for _ in range(self.screen_height)
        ]

    def _resize_if_needed(self) -> bool:
        """Check if terminal was resized and update frames if needed."""
        new_width, new_height = get_terminal_size()
        if new_width != self.screen_width or new_height != self.screen_height:
            self.screen_width = new_width
            self.screen_height = new_height
            self._initialize_frames()
            clear_terminal()
            return True
        return False

    def pipe(self, widget: Widget, x: int, y: int, index: int = 1) -> None:
        """Add a rendered object to the renderer."""
        with self._lock:
            if widget in self._widget_lookup:
                rendered_obj = self._widget_lookup[widget]
                rendered_obj.region = Region(x, y, widget.width, widget.height)
                rendered_obj.index = index
                rendered_obj.dirty = True
                return

            region = Region(x, y, widget.width, widget.height)
            rendered_object = RenderedObject(widget=widget, region=region, index=index)

            self.widgets.append(rendered_object)
            self._widget_lookup[widget] = rendered_object

    def remove_widget(self, widget: Widget) -> None:
        """Remove a widget from the renderer."""
        with self._lock:
            if widget in self._widget_lookup:
                rendered_obj = self._widget_lookup[widget]
                self.widgets.remove(rendered_obj)
                del self._widget_lookup[widget]

                self._clear_widget_area(rendered_obj.region)

    def _clear_widget_area(self, region: Region) -> None:
        """Clear the area where a widget was located."""
        for y in range(region.y, min(region.y + region.height, self.screen_height)):
            for x in range(region.x, min(region.x + region.width, self.screen_width)):
                if 0 <= y < self.screen_height and 0 <= x < self.screen_width:
                    self.current_frame[y][x] = Char(" ")

    def clear(self) -> None:
        """Clear all widgets and frames."""
        with self._lock:
            self.widgets.clear()
            self._widget_lookup.clear()

            for row in self.current_frame:
                row[:] = [Char(" ")] * self.screen_width
            for row in self.previous_frame:
                row[:] = [Char(" ")] * self.screen_width

    def mark_widget_dirty(self, widget: Widget) -> None:
        """Mark a specific widget as dirty for re-rendering."""
        with self._lock:
            if widget in self._widget_lookup:
                self._widget_lookup[widget].dirty = True

    def render(self) -> None:
        """Render all piped widgets to the terminal."""
        try:
            if self._resize_if_needed():
                with self._lock:
                    for rendered_obj in self.widgets:
                        rendered_obj.dirty = True

            with self._lock:
                for row in self.current_frame:
                    row[:] = [Char(" ")] * self.screen_width

                self.widgets.sort(key=lambda obj: obj.index)

                for rendered_object in self.widgets:
                    if not rendered_object.dirty:
                        continue

                    widget: Widget = rendered_object.widget
                    region: Region = rendered_object.region

                    try:
                        widget_content: List[List[Char]] = widget.render()
                        self._render_widget_content(widget_content, region)
                        rendered_object.dirty = False
                    except Exception as e:
                        print(
                            f"Error rendering widget {widget.name}: {e}",
                            file=sys.stderr,
                        )
                        continue

            self._update_terminal()

        except Exception as e:
            print(f"Error in render loop: {e}", file=sys.stderr)

    def _render_widget_content(
        self, widget_content: List[List[Char]], region: Region
    ) -> None:
        """Render widget content to the current frame."""
        for row_index, row in enumerate(widget_content):
            frame_y = region.y + row_index
            if frame_y >= self.screen_height:
                break

            for col_index, char in enumerate(row):
                frame_x = region.x + col_index
                if frame_x >= self.screen_width:
                    break

                if frame_y >= 0 and frame_x >= 0:
                    self.current_frame[frame_y][frame_x] = char

    def _update_terminal(self) -> None:
        """Update only the changed characters in the terminal."""
        changes_made = False

        for y in range(min(len(self.previous_frame), len(self.current_frame))):
            for x in range(
                min(len(self.previous_frame[y]), len(self.current_frame[y]))
            ):
                old_char = self.previous_frame[y][x]
                new_char = self.current_frame[y][x]

                if old_char != new_char:
                    cursor.move(x + 1, y + 1)
                    try:
                        colored_char = colorize(
                            new_char.char, fg=new_char.fg_color, bg=new_char.bg_color
                        )
                        sys.stdout.write(colored_char)
                        changes_made = True
                    except Exception as e:
                        print(f"Error writing character: {e}", file=sys.stderr)
                        continue

        if changes_made:
            sys.stdout.flush()

        self.previous_frame = [row[:] for row in self.current_frame]

    def cleanup(self) -> None:
        """Clean up renderer resources."""
        try:
            cursor.show()
            clear_terminal()
        except Exception as e:
            print(f"Error during cleanup: {e}", file=sys.stderr)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
