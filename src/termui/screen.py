import inspect
from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from termui.errors import ScreenError
from termui.input import Keybind
from termui.utils.terminal_utils import get_terminal_size

if TYPE_CHECKING:
    from termui.app import App
    from termui.layouts._layout import Layout
    from termui.widgets._widget import Widget


class Screen(ABC):
    """A class representing a screen in the terminal UI."""

    def __init__(self) -> None:
        self.name: str = ""
        self.width, self.height = get_terminal_size()
        self._app: Optional["App"] = None
        self._local_keybinds: list[Keybind] = []
        self.widgets: list[Widget] = []
        self.inline: bool = True

    def __str__(self) -> str:
        return f"Screen(name={self.name}, width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def app(self) -> "App":
        """Get the application instance."""
        if self._app is None:
            raise ScreenError("Screen is not mounted to an App instance.")
        return self._app

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

        Parameters
        ----------
        name : str
            The name of the screen.
        width : int
            The width of the screen. Defaults to the terminal's current width.
        height : int
            The height of the screen. Defaults to the terminal's current height.
        inline : bool
            Whether the screen is inline or not. False will resize the terminal
            depending on the given screen size.
        """
        self.name = kwargs.get("name", "Default Screen")
        max_width, max_height = get_terminal_size()
        self.width = kwargs.get("width", max_width)
        self.height = kwargs.get("height", max_height)
        self.inline = kwargs.get("inline", True)

    def get_widget_by_name(self, name: str) -> "Widget | None":
        """Get a widget by its name."""
        for widget in self.widgets:
            if widget.name == name:
                return widget
        return None

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def build(self) -> "Layout":
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

    def mount(self, app: "App") -> None:
        """Mount the screen."""
        self._app = app
        self._setup_local_keybinds()
        for keybind in self.local_keybinds:
            app.input_handler.register_keybind(keybind)

        app.renderer.pipe(self)
        self.app.log.system(f"Mounted screen: {self.name}")

    def unmount(self) -> None:
        """Unmount the screen."""
        self.app.renderer.clear()
        for keybind in self.local_keybinds:
            self.app.input_handler.unregister_keybind(keybind)
