import inspect
from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from termui.color import Color
from termui.dom import DOMNode
from termui.errors import ScreenError
from termui.events import InputEvent, MouseEvent
from termui.input import Keybind
from termui.logger import Logger
from termui.utils.terminal_utils import get_terminal_size
from termui.widget import Widget


if TYPE_CHECKING:
    from termui.app import App
    from termui.layout import Layout


class Screen(ABC):
    """Base class for terminal UI screens.

    A Screen represents a complete UI view that can contain widgets, handle
    input events, and manage its own lifecycle. Screens are mounted to an
    App instance and can have local keybinds.
    """

    def __init__(self) -> None:
        """Initialize the screen with default settings."""
        self.name: str = ""
        """Name of the screen. Used by the application for identification."""
        self.width, self.height = get_terminal_size()
        """Width and height of the screen."""
        self._app: Optional["App"] = None
        """Reference to the app instance this screen belongs to."""
        self._local_keybinds: list[Keybind] = []
        """A list of local keybinds"""
        self.renderables: list[DOMNode] = []
        """A list of renderable DOM nodes for the screen."""
        self.inline: bool = True
        """Whether the screen is inline (True) or should resize the terminal to fit (False)."""
        self.background_color: Optional[Color] = None
        """Optional background color for the screen."""

    def __str__(self) -> str:
        return f"Screen(name={self.name}, width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def app(self) -> "App":
        """Get the application instance.

        Returns:
            The App instance this screen is mounted to.

        Raises:
            ScreenError: If the screen is not mounted to an App instance.
        """
        if self._app is None:
            raise ScreenError("Screen is not mounted to an App instance.")
        return self._app

    @property
    def log(self) -> "Logger":
        """Get the logger instance from the mounted application.

        Returns:
            The Logger instance from the App.

        Raises:
            ScreenError: If the screen is not mounted to an App instance.
        """
        if self._app is None:
            raise ScreenError("Screen is not mounted to an App instance.")
        return self._app.log

    @property
    def local_keybinds(self) -> list[Keybind]:
        """Get the local keybinds for this screen.

        Returns:
            A list of keybinds that are specific to this screen.
        """
        return self._local_keybinds

    def _setup_local_keybinds(self) -> None:
        """Find and register all methods decorated with @keybind.

        Scans all methods of the screen instance for keybind decorations
        and creates Keybind objects for them.
        """
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
        """Initialize the screen with metadata and configuration.

        Args:
            **kwargs: Screen configuration options:
                name: The name of the screen.
                width: The width of the screen. Defaults to terminal width.
                height: The height of the screen. Defaults to terminal height.
                inline: Whether the screen is inline (True) or should resize
                       the terminal to fit (False).
                background_color: Optional background color for the screen.
        """
        self.name = kwargs.get("name", "Default Screen")
        max_width, max_height = get_terminal_size()
        self.width = kwargs.get("width", max_width)
        self.height = kwargs.get("height", max_height)
        self.inline = kwargs.get("inline", True)
        self.background_color = kwargs.get("background_color", None)

    def set_background_color(self, color: Optional[Color]) -> None:
        """Set the background color of the screen.

        Args:
            color: The background color to set. If None, removes the
                  background color.
        """
        self.background_color = color
        if self._app and self._app.renderer:
            self._app.renderer.clear()

    def get_widget_by_name(self, name: str) -> "Widget | None":
        """Get a widget by its name.

        Args:
            name: The name of the widget to find.

        Returns:
            The widget with the matching name, or None if not found.
        """
        for widget in self.renderables:
            if widget.name == name and isinstance(widget, Widget):
                return widget
        return None

    def get_widget_by_id(self, widget_id: str) -> "Widget | None":
        """Get a widget by its ID.

        Args:
            widget_id: The ID of the widget to find.

        Returns:
            The widget with the matching ID, or None if not found.
        """
        for widget in self.renderables:
            if widget.id == widget_id and isinstance(widget, Widget):
                return widget
        return None

    def handle_input_event(self, event: InputEvent) -> None:
        """Handle an input event by forwarding it to appropriate widgets.

        Args:
            event: The input event to handle. Mouse events are forwarded
                  to widgets that contain the mouse position.
        """
        if isinstance(event, MouseEvent):
            for widget in self.renderables:
                if isinstance(widget, Widget):
                    if widget.region.contains(event.x, event.y):
                        widget.handle_mouse_event(event)
                    else:
                        widget._on_mouse_exit()

    @abstractmethod
    def setup(self) -> None:
        """Setup the screen with initial configuration.

        This method is called once when the screen is registered with
        the application. Use this for one-time initialization.
        """
        pass

    @abstractmethod
    def build(self) -> "Layout":
        """Build and return the root layout for this screen.

        This method should create and return the root layout containing
        all widgets for this screen. It's called when the screen is
        mounted and after terminal resizes.

        Returns:
            The root layout widget that contains all screen content.
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the screen dynamically.

        This method is called periodically by the application loop and
        can be used to update screen content, animations, or state
        based on time or other factors.
        """
        pass

    def mount(self, app: "App") -> None:
        """Mount the screen to an application instance.

        Args:
            app: The application instance to mount to.
        """
        self._app = app
        self._setup_local_keybinds()
        for keybind in self.local_keybinds:
            app.input_handler.register_keybind(keybind)

        app.renderer.pipe(self)
        self.app.log.system(f"Mounted screen: {self.name}")

    def unmount(self) -> None:
        """Unmount the screen from its application instance.

        Cleans up the renderer and removes local keybinds from the
        input handler.
        """
        self.app.renderer.clear()
        for keybind in self.local_keybinds:
            self.app.input_handler.unregister_keybind(keybind)
