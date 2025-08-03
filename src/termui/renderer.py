import sys
from typing import Optional

from termui.colors import colorize
from termui.cursor import Cursor as cursor
from termui.dom import DOMNode
from termui.screen import Screen
from termui.types.char import Char
from termui.utils.geometry import Region
from termui.utils.terminal_utils import clear_terminal, get_terminal_size
from termui.widgets._widget import Widget


class Renderer:
    def __init__(self) -> None:
        self.width, self.height = get_terminal_size()
        self.root = None
        self.previous_frame: list[list[Char]] = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]
        self.current_frame: list[list[Char]] = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]
        clear_terminal()
        cursor.hide()

    def construct_dom_tree(self, parent: DOMNode, child: DOMNode) -> None:
        """Construct a DOM tree by adding a child DOMNode to a parent DOMNode."""
        if not isinstance(parent, DOMNode):
            raise TypeError("Parent must be a DOMNode.")
        if not isinstance(child, DOMNode):
            raise TypeError("Child must be a DOMNode.")
        parent.add_child(child)
        if child.children:
            for grandchild in child.children:
                self.construct_dom_tree(child, grandchild)

    def pipe(self, screen: Screen) -> None:
        """Pipe a screen to the renderer."""
        if not isinstance(screen, Screen):
            raise TypeError("Piped object must be a Screen instance.")

        screen_content = screen.build()
        if not isinstance(screen_content, Widget):
            raise TypeError("Screen build method must return a Widget instance.")

        self.root = screen_content
        for child in screen_content.children:
            if not isinstance(child, Widget):
                raise TypeError("All children must be Widget instances.")
            self.construct_dom_tree(self.root, child)

    def print_dom_tree(self, node: Optional[DOMNode] = None, indent: int = 4) -> None:
        """Print the DOM tree starting from the given node."""
        if node is None:
            node = self.root
        if node is None:
            print("No DOM tree to display.")
            return

        print(
            " " * indent
            + f"Node ID: {node.id}, Name: {node.widget.name if node.widget else 'None'}"
        )
        for child in node.children:
            self.print_dom_tree(child, indent + 2)

    def render(self) -> None:
        """Render all piped widgets to the terminal."""
        self.print_dom_tree(self.root)  # Debugging: print the DOM tree structure
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
