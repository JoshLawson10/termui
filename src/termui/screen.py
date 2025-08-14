import inspect
from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from termui.color import Color
from termui.dom import DOMNode
from termui.errors import ScreenError
from termui.events import InputEvent, KeyEvent, MouseEvent
from termui.input import Keybind
from termui.utils.terminal_utils import get_terminal_size
from termui.widgets._widget import Widget


if TYPE_CHECKING:
    from termui.app import App
    from termui.layouts._layout import Layout


class Screen(ABC):
    """A class representing a screen in the terminal UI."""

    def __init__(self) -> None:
        self.name: str = ""
        self.width, self.height = get_terminal_size()
        self._app: Optional["App"] = None
        self._local_keybinds: list[Keybind] = []
        self.renderables: list[DOMNode] = []
        self.inline: bool = True
        self.background_color: Optional[Color] = None

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
    def log(self):
        if self._app is None:
            raise ScreenError("Screen is not mounted to an App instance.")
        return self._app.log

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
        self.background_color = kwargs.get("background_color", None)

    def set_background_color(self, color: Optional[Color]) -> None:
        """Set the background color of the screen.

        Parameters
        ----------
        color : Optional[Color]
            The background color to set. If None, removes the background color.
        """
        self.background_color = color
        if self._app and self._app.renderer:
            self._app.renderer.clear()

    def get_widget_by_name(self, name: str) -> "Widget | None":
        """Get a widget by its name."""
        for widget in self.renderables:
            if widget.name == name and isinstance(widget, Widget):
                return widget
        return None

    def get_widget_by_id(self, widget_id: str) -> "Widget | None":
        """Get a widget by its ID."""
        for widget in self.renderables:
            if widget.id == widget_id and isinstance(widget, Widget):
                return widget
        return None

    def handle_input_event(self, event: InputEvent) -> None:
        """Handle an input event."""
        if isinstance(event, MouseEvent):
            for widget in self.renderables:
                if isinstance(widget, Widget):
                    if widget.region.contains(event.x, event.y):
                        widget.handle_mouse_event(event)

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
