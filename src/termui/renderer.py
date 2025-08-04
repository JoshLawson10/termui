import sys
from typing import TYPE_CHECKING

from termui.colors.colorize import colorize

from termui.cursor import Cursor as cursor
from termui.dom import DOMTree
from termui.screen import Screen
from termui.types.char import Char
from termui.utils.terminal_utils import clear_terminal, get_terminal_size

if TYPE_CHECKING:
    from termui.app import App


class Renderer:
    def __init__(self, app: "App") -> None:
        self.app = app
        self.width, self.height = get_terminal_size()
        self.dom_tree = DOMTree()
        self.count = 0
        clear_terminal()
        cursor.hide()

    def pipe(self, screen: Screen) -> None:
        """Pipe a screen to the renderer."""
        self.app.log.system(f"Piping screen: {screen.name} to renderer")
        screen_root = screen.build()
        screen_root.set_size(self.width, self.height)
        self.dom_tree.set_root(screen_root)

    def render(self) -> None:
        """Render all piped widgets to the terminal."""
        if self.count < 1:
            self.app.log.system(f"self.dom_tree: {self.dom_tree.get_tree_string()}")
            self.count = 1

        clear_terminal()
        current_frame: list[list[Char]] = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]

        for node in self.dom_tree.get_node_list():
            if node.widget is None:
                continue

            widget = node.widget
            region = widget.region

            if (
                region.x < 0
                or region.y < 0
                or region.x + region.width > self.width
                or region.y + region.height > self.height
            ):
                continue

            widget_content: list[list[Char]] = widget.render()
            for row_index, row in enumerate(widget_content):
                for col_index, char in enumerate(row):
                    if (
                        0 <= region.y + row_index < self.height
                        and 0 <= region.x + col_index < self.width
                    ):
                        current_frame[region.y + row_index][region.x + col_index] = char

        for line in current_frame:
            formatted_line: list[str] = []
            for char in line:
                formatted_line.append(
                    colorize(char.char, fg=char.fg_color, bg=char.bg_color)
                )
            sys.stdout.write("".join(formatted_line))

        sys.stdout.flush()

    def clear(self) -> None:
        """Clear the renderer's current frame."""
        self.current_frame = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]
        clear_terminal()
        cursor.move(1, 1)
        self.previous_frame = [row[:] for row in self.current_frame]
        self.root = None
