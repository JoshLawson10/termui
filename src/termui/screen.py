from .layouts.div import Div
from .utils import clear_terminal, get_terminal_size
from .input import InputHandler, Keybind
from abc import ABC, abstractmethod
from typing import Any
import inspect


class Screen(ABC):
    """A class representing a screen in the terminal UI."""

    def __init__(self) -> None:
        self.name: str = ""
        self.width: int
        self.height: int
        self.width, self.height = get_terminal_size()
        self.cols: int = 4
        self.rows: int = 12
        self.cell_width: int = self.width // self.cols
        self.cell_height: int = self.height // self.rows
        self.divs: list[Div] = []
        self._local_keybinds: list[Keybind] = []
        self._input_handler: InputHandler = InputHandler()

    def __str__(self) -> str:
        return f"Screen(name={self.name}, width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def local_keybinds(self) -> list[Keybind]:
        """Get the local keybinds for this screen."""
        return self._local_keybinds

    def _setup_local_keybinds(self):
        """Finds and registers all methods decorated with @keybind."""
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            info = getattr(method, "_keybind_info", None)
            if info is not None:
                keybind_obj = Keybind(
                    key=info["key"],
                    action=method,
                    description=info["description"],
                    visible=info["visible"],
                )
                self._local_keybinds.append(keybind_obj)

    def _update_cell_dimensions(self) -> None:
        """Update the cell dimensions based on the current screen size."""
        self.cell_width = self.width // self.cols
        self.cell_height = self.height // self.rows

    def add(self, div: Div) -> None:
        """Add a Div to the screen."""
        if not isinstance(div, Div):
            raise TypeError("Expected a Div instance.")
        self.divs.append(div)

    def remove(self, div: Div) -> None:
        """Remove a Div from the screen."""
        if div in self.divs:
            self.divs.remove(div)

    def get_div(self, name: str) -> Div | None:
        """Get a Div by its name."""
        for div in self.divs:
            if div.name == name:
                return div
        return None

    def screen_metadata(self, **kwargs: Any) -> None:
        """Initialize the screen.

        Parameters:
            name (str): The name of the screen.
            width (int): The width of the screen. Defaults to the terminal's current width.
            height (int): The height of the screen. Defaults to the terminal's current height.
            cols (int): The number of columns in the screen. Defaults to 4.
            rows (int): The number of rows in the screen. Defaults to 12.
        """
        self.name = kwargs.get("name", "Default Screen")
        max_width, max_height = get_terminal_size()
        self.width = kwargs.get("width", max_width)
        self.height = kwargs.get("height", max_height)
        self.cols = kwargs.get("cols", 4)
        self.rows = kwargs.get("rows", 12)

    @abstractmethod
    def build(self):
        """Setup the screen with initial Divs.

        From within :meth:`Screen.build`, you can add Divs to the screen
        by calling :meth:`Screen.add`, and remove them by calling :meth:`Screen.remove`.
        All Divs currently on the screen will be stored in the :attr:`Screen.divs` list.
        """
        pass

    def mount(self, input_handler: InputHandler) -> None:
        """Mount the screen."""
        self._setup_local_keybinds()
        self._input_handler = input_handler
        for keybind in self.local_keybinds:
            self._input_handler.register_keybind(keybind)
        self._render()

    def unmount(self) -> None:
        """Unmount the screen."""
        for keybind in self.local_keybinds:
            self._input_handler.unregister_keybind(keybind)

    def _render(self) -> None:
        """Render the screen with all Divs."""
        self._update_cell_dimensions()

        screen: list[list[str]] = [
            [" " for _ in range(self.width)] for _ in range(self.height)
        ]

        for div in self.divs:
            cell_span_width: int = div.end_col - div.start_col + 1
            cell_span_height: int = div.end_row - div.start_row + 1

            div_width: int = (cell_span_width) * self.cell_width
            div_height: int = (cell_span_height) * self.cell_height

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
