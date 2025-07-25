from typing import Optional, TYPE_CHECKING

from termui.widgets._widget import Widget

if TYPE_CHECKING:
    from termui.layouts._layout import LayoutManager


class BaseContainerWidget(Widget):
    """A widget that can contain other widgets."""

    def __init__(self, name: Optional[str] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.children: list[Widget] = []
        self.layout_manager: Optional["LayoutManager"] = None

    def add_child(self, child: Widget) -> None:
        """Add a child widget."""
        if child not in self.children:
            self.children.append(child)
            self.mark_dirty()

            if self._render_node:
                child_node = child.get_render_node()
                self._render_node.add_child(child_node)

    def remove_child(self, child: Widget) -> None:
        """Remove a child widget."""
        if child in self.children:
            self.children.remove(child)
            self.mark_dirty()

            if self._render_node and child._render_node:
                self._render_node.remove_child(child._render_node)

    def clear_children(self) -> None:
        """Remove all child widgets."""
        for child in list(self.children):
            self.remove_child(child)

    def set_layout_manager(self, layout_manager: "LayoutManager") -> None:
        """Set the layout manager for this container."""
        self.layout_manager = layout_manager
        self.layout_children()

    def layout_children(self) -> None:
        """Layout all child widgets."""
        if self.layout_manager:
            self.layout_manager.layout(self, self.children)
            self.mark_dirty()

    def get_child_by_name(self, name: str) -> Optional[Widget]:
        """Get a child widget by name."""
        for child in self.children:
            if child.name == name:
                return child
        return None

    def get_child_by_id(self, widget_id: str) -> Optional[Widget]:
        """Get a child widget by ID."""
        for child in self.children:
            if child.id == widget_id:
                return child
        return None
