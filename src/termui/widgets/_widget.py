from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import threading

from termui.types.char import Char


class Widget(ABC):
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.width = 0
        self.height = 0
        self._mounted = False
        self._dirty = True
        self._visible = True
        self._enabled = True
        self._lock = threading.Lock()
        self._parent: Optional["Widget"] = None
        self._children: list["Widget"] = []
        self._event_handlers: Dict[str, list] = {}

    def update_dimensions(self, width: int, height: int) -> None:
        """Update the dimensions of the widget."""
        if width < 0 or height < 0:
            raise ValueError("Width and height must be non-negative")

        with self._lock:
            if self.width != width or self.height != height:
                self.width = width
                self.height = height
                self.mark_dirty()

    def mount(self) -> None:
        """Called when widget is added to screen."""
        with self._lock:
            self._mounted = True
            self.mark_dirty()
            self._on_mount()

    def unmount(self) -> None:
        """Called when widget is removed from screen."""
        with self._lock:
            self._mounted = False
            self._on_unmount()

    def _on_mount(self) -> None:
        """Override this method to perform setup when widget is mounted."""
        pass

    def _on_unmount(self) -> None:
        """Override this method to perform cleanup when widget is unmounted."""
        pass

    def mark_dirty(self) -> None:
        """Mark widget as needing re-render."""
        with self._lock:
            self._dirty = True

    def clear_dirty(self) -> None:
        """Clear the dirty flag."""
        with self._lock:
            self._dirty = False

    @property
    def is_dirty(self) -> bool:
        """Check if widget needs re-rendering."""
        with self._lock:
            return self._dirty

    @property
    def is_mounted(self) -> bool:
        """Check if widget is mounted."""
        with self._lock:
            return self._mounted

    @property
    def visible(self) -> bool:
        """Check if widget is visible."""
        with self._lock:
            return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Set widget visibility."""
        with self._lock:
            if self._visible != value:
                self._visible = value
                self.mark_dirty()

    @property
    def enabled(self) -> bool:
        """Check if widget is enabled."""
        with self._lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set widget enabled state."""
        with self._lock:
            if self._enabled != value:
                self._enabled = value
                self.mark_dirty()

    def add_child(self, child: "Widget") -> None:
        """Add a child widget."""
        with self._lock:
            if child not in self._children:
                self._children.append(child)
                child._parent = self
                self.mark_dirty()

    def remove_child(self, child: "Widget") -> None:
        """Remove a child widget."""
        with self._lock:
            if child in self._children:
                self._children.remove(child)
                child._parent = None
                self.mark_dirty()

    def get_children(self) -> list["Widget"]:
        """Get all child widgets."""
        with self._lock:
            return self._children.copy()

    def get_parent(self) -> Optional["Widget"]:
        """Get parent widget."""
        with self._lock:
            return self._parent

    def add_event_handler(self, event_type: str, handler) -> None:
        """Add an event handler."""
        with self._lock:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            self._event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler) -> None:
        """Remove an event handler."""
        with self._lock:
            if event_type in self._event_handlers:
                try:
                    self._event_handlers[event_type].remove(handler)
                except ValueError:
                    pass

    def emit_event(self, event_type: str, *args, **kwargs) -> None:
        """Emit an event to all handlers."""
        with self._lock:
            handlers = self._event_handlers.get(event_type, []).copy()

        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Error in event handler: {e}")

    def focus(self) -> None:
        """Focus this widget."""
        self.emit_event("focus")

    def blur(self) -> None:
        """Remove focus from this widget."""
        self.emit_event("blur")

    def validate(self) -> bool:
        """Validate widget state. Override in subclasses."""
        return True

    def get_state(self) -> Dict[str, Any]:
        """Get widget state for serialization."""
        with self._lock:
            return {
                "name": self.name,
                "width": self.width,
                "height": self.height,
                "visible": self._visible,
                "enabled": self._enabled,
                "mounted": self._mounted,
                "dirty": self._dirty,
            }

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set widget state from serialized data."""
        with self._lock:
            self.name = state.get("name", self.name)
            self.width = state.get("width", self.width)
            self.height = state.get("height", self.height)
            self._visible = state.get("visible", self._visible)
            self._enabled = state.get("enabled", self._enabled)
            self.mark_dirty()

    @abstractmethod
    def render(self) -> list[list[Char]]:
        """Render the widget."""
        pass

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name}, {self.width}x{self.height})"
        )

    def __repr__(self) -> str:
        return self.__str__()
