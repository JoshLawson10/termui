from abc import abstractmethod
from typing import Any, Optional
import inspect

from termui.widgets._widget import Widget
from termui.widgets._base_container import BaseContainerWidget

from termui.layouts import VerticalLayoutManager
from termui.renderer import Renderer
from termui.input import InputHandler, Keybind
from termui.utils.terminal_utils import get_terminal_size

from termui.utils.terminal_utils import get_terminal_size


class Screen(BaseContainerWidget):
    """A class representing a screen in the terminal UI."""

    def __init__(self, name: Optional[str] = None, **kwargs) -> None:
        width, height = get_terminal_size()
        super().__init__(name=name, width=width, height=height, **kwargs)

        self.screen_name = name or f"Screen_{self.id[:8]}"
        self._local_keybinds: list[Keybind] = []
        self._input_handler: Optional[InputHandler] = None
        self._renderer: Optional[Renderer] = None
        self._is_mounted = False

        self.set_layout_manager(VerticalLayoutManager())
        self.setup()

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
        """Configure screen metadata (for backward compatibility)."""
        if "name" in kwargs:
            self.screen_name = kwargs["name"]
            self.name = kwargs["name"]

        max_width, max_height = get_terminal_size()
        new_width = kwargs.get("width", max_width)
        new_height = kwargs.get("height", max_height)

        if new_width != self.width or new_height != self.height:
            self.set_size(new_width, new_height)

    def get_widget_by_name(self, name: str) -> Optional[Widget]:
        """Get a widget by its name (searches recursively)."""

        def search_widget(widget: Widget, target_name: str) -> Optional[Widget]:
            if widget.name == target_name:
                return widget

            if isinstance(widget, BaseContainerWidget):
                for child in widget.children:
                    result = search_widget(child, target_name)
                    if result:
                        return result

            return None

        return search_widget(self, name)

    def get_widget_by_id(self, widget_id: str) -> Optional[Widget]:
        """Get a widget by its ID (searches recursively)."""

        def search_widget(widget: Widget, target_id: str) -> Optional[Widget]:
            if widget.id == target_id:
                return widget

            if isinstance(widget, BaseContainerWidget):
                for child in widget.children:
                    result = search_widget(child, target_id)
                    if result:
                        return result

            return None

        return search_widget(self, widget_id)

    def add_widget(self, widget: Widget) -> None:
        """Add a widget to the screen."""
        self.add_child(widget)

    def remove_widget(self, widget: Widget) -> None:
        """Remove a widget from the screen."""
        self.remove_child(widget)

    def clear_widgets(self) -> None:
        """Remove all widgets from the screen."""
        self.clear_children()

    @abstractmethod
    def setup(self) -> None:
        """Set up the screen (called during initialization)."""
        pass

    @abstractmethod
    def build(self) -> None:
        """Build the screen content. Should add widgets using add_widget()."""
        pass

    @abstractmethod
    def update(self) -> None:
        """Update the screen dynamically (called each frame)."""
        pass

    def render(self) -> list[list[Any]]:
        """Render the screen (container renders its background/border if any)."""
        return [[]]

    def mount(self, input_handler: InputHandler, renderer: Renderer) -> None:
        """Mount the screen with input handler and renderer."""
        if self._is_mounted:
            return

        self._setup_local_keybinds()
        self._input_handler = input_handler
        self._renderer = renderer

        for keybind in self.local_keybinds:
            self._input_handler.register_keybind(keybind)

        self.width, self.height = get_terminal_size()
        self.build()
        self.layout_children()
        self._register_widgets_with_renderer(self)
        self._is_mounted = True

    def unmount(self) -> None:
        """Unmount the screen."""
        if not self._is_mounted:
            return

        if self._input_handler:
            for keybind in self.local_keybinds:
                self._input_handler.unregister_keybind(keybind)

        if self._renderer:
            self._unregister_widgets_from_renderer(self)

        self._is_mounted = False

    def _register_widgets_with_renderer(
        self, widget: Widget, parent_id: str = "root"
    ) -> None:
        """Recursively register widgets with the renderer."""
        if not self._renderer:
            return

        self._renderer.register_renderable(widget, parent_id)

        if isinstance(widget, BaseContainerWidget):
            for child in widget.children:
                self._register_widgets_with_renderer(child, widget.id)

    def _unregister_widgets_from_renderer(self, widget: Widget) -> None:
        """Recursively unregister widgets from the renderer."""
        if not self._renderer:
            return

        if isinstance(widget, BaseContainerWidget):
            for child in widget.children:
                self._unregister_widgets_from_renderer(child)

        self._renderer.unregister_renderable(widget.id)

    def refresh(self) -> None:
        """Refresh the screen layout and rendering."""
        if self._is_mounted:
            new_width, new_height = get_terminal_size()
            if new_width != self.width or new_height != self.height:
                self.set_size(new_width, new_height)
                self.layout_children()

            self.update()
            self.mark_dirty()

    def on_resize(self, width: int, height: int) -> None:
        """Called when the screen is resized."""
        self.set_size(width, height)
        self.layout_children()

    def focus_widget(self, widget: Widget) -> None:
        """Focus a specific widget (placeholder for future focus management)."""
        # TODO: Implement focus management
        pass

    def get_focused_widget(self) -> Optional[Widget]:
        """Get the currently focused widget (placeholder)."""
        # TODO: Implement focus management
        return None
