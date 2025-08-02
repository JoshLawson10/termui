import inspect
from abc import ABC, abstractmethod
from typing import Any

from termui.input import InputHandler, Keybind

from termui.layouts.layout import Layout
from termui.renderer import Renderer

from termui.utils.terminal_utils import get_terminal_size
from termui.widgets._widget import Widget


class Screen(ABC):
    """A class representing a screen in the terminal UI."""

    def __init__(self) -> None:
        self.name: str = ""
        self.width: int
        self.height: int
        self.width, self.height = get_terminal_size()
        self._local_keybinds: list[Keybind] = []
        self._input_handler: InputHandler = InputHandler()
        self._renderer: Renderer = Renderer()
        self.widgets: list[Widget] = []

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

    def get_widget_by_name(self, name: str) -> Widget | None:
        """Get a widget by its name."""
        for widget in self.widgets:
            if widget.name == name:
                return widget
        return None

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def build(self) -> Layout:
        """Setup the screen with initial Divs.

        From within :meth:`Screen.build`, you can add Divs to the screen
        by calling :meth:`Screen.add`, and remove them by calling :meth:`Screen.remove`.
        All Divs currently on the screen will be stored in the :attr:`Screen.divs` list.
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the screen dynamically.

        This method can be used to update the screen content or state.
        It is called periodically by the application loop.
        """
        pass

    def _unpack_and_pipe_layout(self, layout: Layout) -> None:
        """Unpack the screen's layout and pipe its widgets to the renderer."""

        for placement in layout.placements:
            child = placement.child
            if isinstance(child, Widget):
                if child not in self.widgets:
                    self._renderer.pipe(
                        child,
                        placement.region.x,
                        placement.region.y,
                    )
                    self.widgets.append(child)
            elif isinstance(child, Layout):
                child.update_dimensions(placement.region.width, placement.region.height)
                self._unpack_and_pipe_layout(child)
            else:
                raise TypeError(f"Child {child} is not a Widget or Layout instance.")

    def mount(self, input_handler: InputHandler, renderer: Renderer) -> None:
        """Mount the screen."""
        self._setup_local_keybinds()
        self._input_handler = input_handler
        self._renderer = renderer
        for keybind in self.local_keybinds:
            self._input_handler.register_keybind(keybind)

        self.width, self.height = get_terminal_size()
        layout: Layout = self.build()
        layout.update_dimensions(self.width, self.height)
        layout.arrange()
        self._unpack_and_pipe_layout(layout)

    def unmount(self) -> None:
        """Unmount the screen."""
        self._renderer.clear()
        for keybind in self.local_keybinds:
            self._input_handler.unregister_keybind(keybind)
