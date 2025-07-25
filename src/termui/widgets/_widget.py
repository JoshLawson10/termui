from abc import abstractmethod
from typing import Optional, Any
import uuid

from termui.types.char import Char
from termui.utils.geometry import Region
from termui.renderer import RenderNode, Renderable


class Widget(Renderable):
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: Optional[str] = None, **kwargs) -> None:
        self.id = kwargs.get("id", str(uuid.uuid4()))
        self.name = name or f"Widget_{self.id[:8]}"

        self.width = kwargs.get("width", 0)
        self.height = kwargs.get("height", 0)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)

        self.visible = kwargs.get("visible", True)
        self.z_index = kwargs.get("z_index", 0)
        self.clip_to_parent = kwargs.get("clip_to_parent", True)

        self._dirty = True
        self._render_node: Optional[RenderNode] = None
        self._props: dict[str, Any] = {}

    def get_render_node(self) -> RenderNode:
        """Get or create the render node for this widget."""
        if self._render_node is None:
            self._render_node = RenderNode(
                id=self.id,
                region=Region(self.x, self.y, self.width, self.height),
                z_index=self.z_index,
                visible=self.visible,
                clip_to_parent=self.clip_to_parent,
            )
        return self._render_node

    def update_render_node(self, node: RenderNode) -> None:
        """Update the render node's content."""
        # Update node properties
        node.region = Region(self.x, self.y, self.width, self.height)
        node.visible = self.visible
        node.z_index = self.z_index
        node.clip_to_parent = self.clip_to_parent

        # Render content
        if self.visible:
            node.content = self.render()
        else:
            node.content = []

        node.dirty = False

    def set_position(self, x: int, y: int) -> None:
        """Set the widget's position."""
        if self.x != x or self.y != y:
            self.x = x
            self.y = y
            self.mark_dirty()

    def set_size(self, width: int, height: int) -> None:
        """Set the widget's size."""
        if self.width != width or self.height != height:
            self.width = width
            self.height = height
            self.mark_dirty()

    def set_bounds(self, x: int, y: int, width: int, height: int) -> None:
        """Set position and size in one call."""
        if self.x != x or self.y != y or self.width != width or self.height != height:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.mark_dirty()

    def show(self) -> None:
        """Show the widget."""
        if not self.visible:
            self.visible = True
            self.mark_dirty()

    def hide(self) -> None:
        """Hide the widget."""
        if self.visible:
            self.visible = False
            self.mark_dirty()

    def mark_dirty(self) -> None:
        """Mark the widget as needing re-render."""
        self._dirty = True
        if self._render_node:
            self._render_node.mark_dirty()

    def is_dirty(self) -> bool:
        """Check if the widget needs re-rendering."""
        return self._dirty

    def set_prop(self, key: str, value: Any) -> None:
        """Set a custom property and mark dirty if changed."""
        if self._props.get(key) != value:
            self._props[key] = value
            self.mark_dirty()

    def get_prop(self, key: str, default: Any = None) -> Any:
        """Get a custom property."""
        return self._props.get(key, default)

    def update_dimensions(self, width: int, height: int) -> None:
        """Update the dimensions of the widget (legacy compatibility)."""
        self.set_size(width, height)

    @abstractmethod
    def render(self) -> list[list[Char]]:
        """Render the widget content."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
