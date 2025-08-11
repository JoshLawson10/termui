import sys
from typing import Optional, TYPE_CHECKING

from termui.char import Char

from termui.color import Color, colorize
from termui.cursor import Cursor as cursor
from termui.dom import DOMTree
from termui.screen import Screen
from termui.utils.geometry import Region
from termui.utils.terminal_utils import (
    clear_terminal,
    get_terminal_size,
    set_terminal_size,
)

if TYPE_CHECKING:
    from termui.app import App


class FrameBuffer:
    """A class to hold the current frame buffer for rendering."""

    def __init__(
        self,
        width: int,
        height: int,
        background_color: Optional[Color] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.background_color = background_color
        self._create_empty_char()
        self.current_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]
        self.previous_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]
        self.dirty_regions: set[tuple[int, int, int, int]] = set()  # (x, y, w, h)
        self.inline: bool = True

    def _create_empty_char(self) -> None:
        """Create the base empty character with background color."""
        self._empty_char = Char(" ", None, self.background_color)

    def _get_empty_char(self) -> Char:
        """Get a new empty character with the current background color."""
        return Char(" ", None, self.background_color)

    def set_size(self, width: int, height: int) -> None:
        """Set the size of the frame buffer."""
        self.width = width
        self.height = height
        self.current_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]
        self.previous_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]

    def set_background_color(self, color: Optional[Color]) -> None:
        """Set the background color of the frame buffer."""
        self.background_color = color
        self._create_empty_char()
        for row in self.current_frame:
            for i, char in enumerate(row):
                if char.char == " " and char.fg_color is None:
                    row[i] = self._get_empty_char()
        self.mark_entire_screen_dirty()

    def mark_entire_screen_dirty(self) -> None:
        """Mark the entire screen as dirty."""
        self.dirty_regions.add((0, 0, self.width, self.height))

    def mark_region_dirty(self, region: Region) -> None:
        """Mark a specific region as dirty."""
        x = max(0, region.x)
        y = max(0, region.y)
        w = min(region.width, self.width - x)
        h = min(region.height, self.height - y)

        if w > 0 and h > 0:
            self.dirty_regions.add((x, y, w, h))

    def clear(self) -> None:
        """Clear the current frame."""
        for row in self.current_frame:
            for i in range(len(row)):
                row[i] = self._get_empty_char()
        self.mark_entire_screen_dirty()

    def draw_char(self, x: int, y: int, char: Char) -> None:
        """Draw a character at the specified position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if char.bg_color is None and self.background_color is not None:
                char = Char(char.char, char.fg_color, self.background_color)

            if self.current_frame[y][x] != char:
                self.current_frame[y][x] = char
                self.mark_region_dirty(Region(x, y, 1, 1))

    def draw_content(
        self, region: Region, content: list[list[Char]], clip: bool = True
    ) -> None:
        """Draw content to the frame buffer."""
        abs_x, abs_y = region.x, region.y

        for row_idx, row in enumerate(content):
            y = abs_y + row_idx
            if clip and (y < 0 or y >= self.height):
                continue

            for col_idx, char in enumerate(row):
                x = abs_x + col_idx
                if clip and (x < 0 or x >= self.width):
                    continue

                if 0 <= x < self.width and 0 <= y < self.height:
                    if char.bg_color is None and self.background_color is not None:
                        char = Char(char.char, char.fg_color, self.background_color)

                    if self.current_frame[y][x] != char:
                        self.current_frame[y][x] = char

        self.mark_region_dirty(region)

    def render_to_terminal(self) -> None:
        """Render only dirty regions to the terminal."""
        if not self.dirty_regions:
            return

        if not self.inline:
            set_terminal_size(self.width, self.height)

        for y in range(self.height):
            for x in range(self.width):
                current_char = self.current_frame[y][x]
                previous_char = self.previous_frame[y][x]

                if current_char != previous_char:
                    cursor.move_no_flush(x + 1, y + 1)
                    sys.stdout.write(
                        colorize(
                            current_char.char,
                            fg=current_char.fg_color,
                            bg=current_char.bg_color,
                        )
                    )

        sys.stdout.flush()

        for y in range(self.height):
            for x in range(self.width):
                self.previous_frame[y][x] = self.current_frame[y][x]

        self.dirty_regions.clear()


class Renderer:
    def __init__(self, app: "App") -> None:
        self.app = app
        self.initial_width, self.initial_height = get_terminal_size()
        self.dom_tree = DOMTree()
        self.frame_buffer = FrameBuffer(self.initial_width, self.initial_height)
        clear_terminal()
        cursor.hide()

    def check_resize(self) -> None:
        """Check if the terminal size has changed and update the renderer."""
        new_width, new_height = get_terminal_size()
        if (new_width, new_height) != (self.width, self.height):
            self.width, self.height = new_width, new_height
            self.frame_buffer = FrameBuffer(
                self.width, self.height, self.frame_buffer.background_color
            )
            if self.dom_tree.root and self.dom_tree.root.widget:
                self.dom_tree.root.widget.set_size(self.width, self.height)

    def pipe(self, screen: Screen) -> None:
        """Pipe a screen to the renderer."""
        self.app.log.system(f"Piping screen: {screen.name} to renderer")
        screen_root = screen.build()
        screen_root.set_size(screen.width, screen.height)
        self.dom_tree.set_root(screen_root)
        self.clear()

        self.frame_buffer.set_size(screen.width, screen.height)
        self.frame_buffer.set_background_color(screen.background_color)
        self.frame_buffer.inline = screen.inline

        self.app.log.system(
            f"Screen {screen.name} DOM Heirarchy: \n {self.dom_tree.get_tree_string()}"
        )

    def render(self) -> None:
        """Render all piped widgets to the terminal."""
        for node in self.dom_tree.get_node_list():
            if node.widget is None or node.dirty == False:
                continue

            self.frame_buffer.draw_content(node.widget.region, node.widget.render())

        self.frame_buffer.render_to_terminal()

    def clear(self) -> None:
        """Clear the renderer's current frame."""
        self.frame_buffer.clear()
