import os
from .div import Div
from ._utils import clear_terminal
from abc import ABC, abstractmethod
from typing import Any


class Screen(ABC):
    """A class representing a screen in the terminal UI."""

    def __init__(self) -> None:
        self.name: str = ""
        self.width: int = os.get_terminal_size().columns
        self.height: int = os.get_terminal_size().lines
        self.cols: int = 4
        self.rows: int = 12
        self.cell_width: int = self.width // self.cols
        self.cell_height: int = self.height // self.rows
        self.divs: list[Div] = []

    def __str__(self) -> str:
        return f"Screen(name={self.name}, width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        return self.__str__()

    def add(self, div: Div) -> None:
        """Add a Div to the screen."""
        if not isinstance(div, Div):
            raise TypeError("Expected a Div instance.")
        self.divs.append(div)

    def remove(self, div: Div) -> None:
        """Remove a Div from the screen."""
        if div in self.divs:
            self.divs.remove(div)

    def initialize_screen(self, **kwargs: Any) -> None:
        """Initialize the screen.

        Parameters:
            name (str): The name of the screen.
            width (int): The width of the screen. Defaults to the terminal's current width.
            height (int): The height of the screen. Defaults to the terminal's current height.
            cols (int): The number of columns in the screen. Defaults to 4.
            rows (int): The number of rows in the screen. Defaults to 12.
        """
        self.name = kwargs.get("name", "Default Screen")
        self.width = kwargs.get("width", os.get_terminal_size().columns)
        self.height = kwargs.get("height", os.get_terminal_size().lines)
        self.cols = kwargs.get("cols", 4)
        self.rows = kwargs.get("rows", 12)

    @abstractmethod
    def setup(self) -> None:
        """Setup the screen with initial Divs.

        From within :meth:`Screen.setup`, you can add Divs to the screen
        by calling :meth:`Screen.add`, and remove them by calling :meth:`Screen.remove`.
        All Divs currently on the screen will be stored in the :attr:`Screen.divs` list.
        """
        pass

    def render(self) -> None:
        """Render the screen with all Divs."""
        screen: list[list[str]] = [
            [" " for _ in range(self.width)] for _ in range(self.height)
        ]

        for div in self.divs:
            cell_span_width: int = div.end_col - div.start_col
            cell_span_height: int = div.end_row - div.start_row

            div_width: int = (cell_span_width) * self.cell_width
            div_height: int = (cell_span_height + 1) * self.cell_height

            div_content: list[list[str]] = div.render(
                width=div_width,
                height=div_height,
            )

            start_x: int = (div.start_col - 1) * self.cell_width
            start_y: int = (div.start_row - 1) * self.cell_height

            for i in range(min(len(div_content), div_height)):
                if start_y + i >= self.height:
                    break
                for j in range(min(len(div_content[i]), div_width)):
                    if start_x + j >= self.width:
                        break
                    if div_content[i][j] != " ":
                        screen[start_y + i][start_x + j] = div_content[i][j]

        clear_terminal()
        for row in screen:
            print("".join(row))
