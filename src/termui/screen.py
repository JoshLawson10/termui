import inspect
from abc import ABC, abstractmethod
from os import get_terminal_size
from typing import Optional, TYPE_CHECKING

from termui._context_manager import input_handler, log, renderer

from termui.color import Color
from termui.dom import DOMNode
from termui.events import InputEvent, MouseEvent
from termui.input import Keybind
from termui.widget import Widget


if TYPE_CHECKING:
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
    def local_keybinds(self) -> list[Keybind]:
        """Get the local keybinds for this screen.

        Returns:
            A list of keybinds that are specific to this screen.
        """
        return self._local_keybinds

    @property
    def log(self):
        """Get the application's logger."""
        return log

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

    def screen_metadata(
        self,
        *,
        name: str = "DefaultScreen",
        width: Optional[int] = None,
        height: Optional[int] = None,
        inline: bool = True,
        background_color: Optional[Color] = None,
    ) -> None:
        """Initialize the screen with metadata and configuration.

        Args:
            name: The name of the screen.
            width: The width of the screen.
            height: The height of the screen.
            inline: Whether the screen is inline (True) or should resize
                   the terminal to fit (False).
            background_color: Optional background color for the screen.
        """
        self.name = name
        max_width, max_height = get_terminal_size()
        self.width = width or max_width
        self.height = height or max_height
        self.inline = inline
        self.background_color = background_color

    def set_background_color(self, color: Optional[Color]) -> None:
        """Set the background color of the screen.

        Args:
            color: The background color to set. If None, removes the
                  background color.
        """
        self.background_color = color
        renderer.clear()

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
                    widget.handle_mouse_event(event)

    @abstractmethod
    def setup(self) -> None:
        """Setup the screen with initial configuration.

        This method is called once when the screen is registered with
        the application. Use this for one-time initialization.
        """
        raise NotImplementedError("Subclasses must implement the setup method.")

    @abstractmethod
    def build(self) -> "Layout":
        """Build and return the root layout for this screen.

        This method should create and return the root layout containing
        all widgets for this screen. It's called when the screen is
        mounted and after terminal resizes.

        Returns:
            The root layout widget that contains all screen content.
        """
        raise NotImplementedError("Subclasses must implement the build method.")

    @abstractmethod
    def update(self) -> None:
        """Update the screen dynamically.

        This method is called periodically by the application loop and
        can be used to update screen content, animations, or state
        based on time or other factors.
        """
        raise NotImplementedError("Subclasses must implement the update method.")

    def mount(self) -> None:
        """Mount the screen to an application instance."""
        self._setup_local_keybinds()
        for keybind in self.local_keybinds:
            input_handler.register_keybind(keybind)

        renderer.pipe(self)
        log.system(f"Mounted screen: {self.name}. Is inline: {self.inline}")

    def unmount(self) -> None:
        """Unmount the screen from its application instance.

        Cleans up the renderer and removes local keybinds from the
        input handler.
        """
        renderer.clear()
        for keybind in self.local_keybinds:
            input_handler.unregister_keybind(keybind)
