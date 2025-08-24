import sys
from os import get_terminal_size
from typing import Optional

from termui._context_manager import app, log

from termui.char import Char
from termui.color import Color, colorize
from termui.cursor import Cursor as cursor
from termui.dom import DOMTree
from termui.screen import Screen
from termui.utils.geometry import Region
from termui.utils.terminal_utils import clear_terminal, set_terminal_size


class FrameBuffer:
    """A double-buffered frame buffer for efficient terminal rendering.

    The FrameBuffer maintains current and previous frame states to enable
    differential rendering, only updating characters that have changed.
    """

    def __init__(
        self,
        width: int,
        height: int,
        background_color: Optional[Color] = None,
    ) -> None:
        """Initialize the frame buffer with specified dimensions.

        Args:
            width: The width of the frame buffer in characters.
            height: The height of the frame buffer in characters.
            background_color: Optional background color for empty cells.
        """
        self.width = width
        self.height = height
        """Width and height of the frame buffer."""
        self.background_color = background_color
        """Background color of the frame buffer."""

        self._create_empty_char()
        self.current_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]
        """The currently rendered frame."""
        self.previous_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]
        """The previous rendered frame."""
        self.dirty_regions: set[tuple[int, int, int, int]] = set()  # (x, y, w, h)
        """Any regions of the screen marked as needing re-rendering."""
        self.inline: bool = True
        """Whether to resize the terminal to the content size.
        Determined by 'screen.inline' in the renderer.
        """

    def _create_empty_char(self) -> None:
        """Create the base empty character with background color."""
        self._empty_char = Char(" ", None, self.background_color)

    def _get_empty_char(self) -> Char:
        """Get a new empty character with the current background color.

        Returns:
            A new Char instance representing an empty space with the
            current background color.
        """
        return Char(" ", None, self.background_color)

    def set_size(self, width: int, height: int) -> None:
        """Set the size of the frame buffer.

        Args:
            width: New width in characters.
            height: New height in characters.
        """
        self.width = width
        self.height = height
        self.current_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]
        self.previous_frame = [
            [self._get_empty_char() for _ in range(width)] for _ in range(height)
        ]

    def set_background_color(self, color: Optional[Color]) -> None:
        """Set the background color of the frame buffer.

        Args:
            color: The new background color, or None to remove background color.
        """
        self.background_color = color
        self._create_empty_char()
        for row in self.current_frame:
            for i, char in enumerate(row):
                if char.char == " " and char.fg_color is None:
                    row[i] = self._get_empty_char()
        self.mark_entire_screen_dirty()

    def mark_entire_screen_dirty(self) -> None:
        """Mark the entire screen as dirty for full redraw."""
        self.dirty_regions.add((0, 0, self.width, self.height))

    def mark_region_dirty(self, region: Region) -> None:
        """Mark a specific region as dirty for redraw.

        Args:
            region: The region to mark as dirty. Coordinates are clamped
                   to the frame buffer boundaries.
        """
        x = max(0, region.x)
        y = max(0, region.y)
        w = min(region.width, self.width - x)
        h = min(region.height, self.height - y)

        if w > 0 and h > 0:
            self.dirty_regions.add((x, y, w, h))

    def clear(self) -> None:
        """Clear the current frame buffer to empty characters."""
        for row in self.current_frame:
            for i, _ in enumerate(row):
                row[i] = self._get_empty_char()
        self.mark_entire_screen_dirty()

    def draw_char(self, x: int, y: int, char: Char) -> None:
        """Draw a character at the specified position.

        Args:
            x: The x-coordinate to draw at.
            y: The y-coordinate to draw at.
            char: The character to draw.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            if char.bg_color is None and self.background_color is not None:
                char = Char(char.char, char.fg_color, self.background_color)

            if self.current_frame[y][x] != char:
                self.current_frame[y][x] = char
                self.mark_region_dirty(Region(x, y, 1, 1))

    def draw_content(
        self, region: Region, content: list[list[Char]], clip: bool = True
    ) -> None:
        """Draw content to the frame buffer.

        Args:
            region: The region where the content should be drawn.
            content: A 2D list of Char objects representing the content.
            clip: Whether to clip content to the frame buffer boundaries.
        """
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
        """Render only changed characters to the terminal.

        Uses differential rendering to only update characters that have
        changed since the last frame, improving performance.
        """
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
    """Main renderer that manages frame buffers and screen rendering.

    The Renderer coordinates between the application, screens, and the terminal,
    handling frame buffering, screen changes, and terminal resizing.
    """

    def __init__(self) -> None:
        """Initialize the renderer with an application instance."""
        self.initial_width, self.initial_height = get_terminal_size()
        """Initial terminal dimensions."""
        self.dom_tree = DOMTree()
        """The DOM tree representing the current screen's UI."""
        self.frame_buffer = FrameBuffer(self.initial_width, self.initial_height)
        """The frame buffer instance for rendering the screen."""

        clear_terminal()
        cursor.hide()

    def check_resize(self) -> bool:
        """Check if the terminal size has changed and update accordingly.

        Returns:
            True if the terminal was resized, False otherwise.
        """
        new_width, new_height = get_terminal_size()
        if (new_width, new_height) != (
            self.frame_buffer.width,
            self.frame_buffer.height,
        ):
            self.frame_buffer = FrameBuffer(
                new_width, new_height, self.frame_buffer.background_color
            )
            if app.current_screen:
                app.current_screen.width = new_width
                app.current_screen.height = new_height

                self.pipe(app.current_screen)

            clear_terminal()
            self.frame_buffer.mark_entire_screen_dirty()

            return True
        return False

    def pipe(self, screen: Screen) -> None:
        """Pipe a screen to the renderer for display.

        Args:
            screen: The screen to prepare for rendering.
        """
        log.system(f"Piping screen: {screen.name} to renderer")

        screen_root = screen.build()
        screen_root.set_size(screen.width, screen.height)
        screen_root.arrange()
        self.dom_tree.set_root(screen_root)
        self.clear()

        screen.renderables = self.dom_tree.get_node_list()

        self.frame_buffer.set_size(screen.width, screen.height)
        self.frame_buffer.set_background_color(screen.background_color)
        self.frame_buffer.inline = screen.inline

        log.system(f"DOM Tree: \n {self.dom_tree.get_tree_string()}")

    def render(self) -> None:
        """Render all widgets to the terminal.

        Processes the DOM tree and renders all dirty widgets to the frame buffer,
        then outputs the changes to the terminal.
        """
        if self.check_resize():
            pass

        for node in self.dom_tree.get_node_list():
            if node.widget is None or node.dirty is False:
                continue

            self.frame_buffer.draw_content(node.widget.region, node.widget.render())

        self.frame_buffer.render_to_terminal()

    def clear(self) -> None:
        """Clear the renderer's current frame and terminal display."""
        self.frame_buffer.clear()
        clear_terminal()
