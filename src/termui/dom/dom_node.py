from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from termui.widget import Widget


@dataclass
class DOMNode:
    """A node in the DOM tree representing a widget hierarchy.

    Args:
        id: Unique identifier for the node.
        name: Optional display name for the node.
        widget: The widget associated with this node, if any.
        parent: Parent node in the DOM tree.
        children: List of child nodes.
        dirty: Whether the node needs re-rendering.
    """

    id: str
    """Unique identifier for the node."""
    name: Optional[str] = field(default_factory=str)
    """Optional display name for the node."""
    widget: Optional["Widget"] = None
    """The widget associated with this node, if any."""
    parent: Optional["DOMNode"] = None
    """The parent node in the DOM tree."""
    children: list["DOMNode"] = field(default_factory=list)
    """The child nodes in the DOM tree."""
    dirty: bool = True
    """Whether the node needs re-rendering."""

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"DOMNode(id={self.id!r}, children={len(self.children)})"

    def set_widget(self, widget: "Widget") -> None:
        """Set the widget associated with this node.

        Args:
            widget: The widget to associate with this node.
        """
        self.widget = widget

    def set_parent(self, parent: "DOMNode") -> None:
        """Set the parent node for this node.

        Args:
            parent: The parent node to set.
        """
        self.parent = parent

    def add_child(self, child: "DOMNode") -> None:
        """Add a child node to this node.

        Args:
            child: The child node to add. Its parent will be set to this node.
        """
        child.parent = self
        self.children.append(child)

    def add_children(self, *children: "DOMNode") -> None:
        """Add multiple child nodes to this node.

        Args:
            *children: The child nodes to add. Their parent will be set to this node.
        """
        for child in children:
            child.parent = self
            self.children.append(child)

    def remove_child(self, child: "DOMNode") -> None:
        """Remove a child node from this node.

        Args:
            child: The child node to remove. Its parent will be set to None.
        """
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def mark_dirty(self) -> None:
        """Mark this node as dirty, indicating it needs to be re-rendered."""
        self.dirty = True

    def mark_dirty_cascade_up(self) -> None:
        """Mark this node and all its ancestors as dirty.

        Propagates the dirty flag up the DOM tree to ensure parent
        nodes are also re-rendered when a child changes.
        """
        self.mark_dirty()
        if self.parent:
            self.parent.mark_dirty_cascade_up()

    def mark_dirty_cascade_down(self) -> None:
        """Mark this node and all its descendants as dirty.

        Propagates the dirty flag down the DOM tree to ensure all
        child nodes are re-rendered when a parent changes.
        """
        self.mark_dirty()
        for child in self.children:
            child.mark_dirty_cascade_down()
