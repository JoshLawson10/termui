import sys
from typing import Optional, TYPE_CHECKING

from termui.cursor import Cursor as cursor
from termui.dom import DOMNode, DOMTree
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
        self.previous_frame: list[list[Char]] = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]
        self.current_frame: list[list[Char]] = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]
        # clear_terminal()
        # cursor.hide()

    def pipe(self, screen: Screen) -> None:
        """Pipe a screen to the renderer."""
        self.app.log.system(f"Piping screen: {screen.name} to renderer")
        screen_root = screen.build()
        self.dom_tree.set_root(screen_root)

    def render(self) -> None:
        """Render all piped widgets to the terminal."""
        self.app.log.system("Rendering DOM tree...")
        self.app.log.system(self.dom_tree.get_tree_string(self.dom_tree.root))
        """ for row in self.current_frame:
            row[:] = [Char(" ")] * self.width

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
                        0 <= region.y + row_index < self.height
                        and 0 <= region.x + col_index < self.width
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
                cursor.move(x + 1, y + 1)
                sys.stdout.write(
                    colorize(new_char.char, fg=new_char.fg_color, bg=new_char.bg_color)
                )

        sys.stdout.flush()
        self.previous_frame = [row[:] for row in self.current_frame] """

    def clear(self) -> None:
        """Clear the renderer's current frame."""
        self.current_frame = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]
        clear_terminal()
        cursor.move(1, 1)
        self.previous_frame = [row[:] for row in self.current_frame]
        self.root = None
