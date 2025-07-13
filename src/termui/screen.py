from abc import ABC, abstractmethod
from typing import Any
import inspect

from termui.layouts.layout import Layout
from termui.widgets.base import Widget
from termui.input import InputHandler, Keybind

from termui.utils import clear_terminal, get_terminal_size


class Screen(ABC):
    """A class representing a screen in the terminal UI."""

    def __init__(self) -> None:
        self.name: str = ""
        self.width: int
        self.height: int
        self.width, self.height = get_terminal_size()
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

    @abstractmethod
    def build(self) -> Layout:
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
        """Render the screen."""
        clear_terminal()
        layout: Layout = self.build()
        layout.update_dimensions(self.width, self.height)
        layout.arrange()

        for placement in layout.placements:
            child = placement.child
            if isinstance(child, Widget):
                child.update_dimensions(placement.region.width, placement.region.height)
                child.render()
            else:
                raise TypeError(f"Child {child} is not a Widget instance.")
