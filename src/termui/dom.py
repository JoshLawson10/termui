from collections import deque
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


class DOMTree:
    """A DOM tree for managing widget hierarchies and rendering order.

    The DOMTree maintains a hierarchical structure of widgets and provides
    methods for traversal, manipulation, and debugging.
    """

    def __init__(self):
        """Initialize an empty DOM tree."""
        self.root: Optional[DOMNode] = None
        self.nodes: set[DOMNode] = set()
        self.nodes_by_id: dict[str, DOMNode] = {}

    def set_root(self, root: DOMNode) -> None:
        """Set the root of the DOM tree.

        Args:
            root: The node to set as the root of the tree.
        """
        self.root = root
        self.nodes.add(root)
        self.nodes_by_id[root.id] = root

    def add_node(self, parent: DOMNode, child: DOMNode) -> None:
        """Add a node to the DOM tree.

        Args:
            parent: The parent node to add the child to.
            child: The child node to add.

        Raises:
            ValueError: If a node with the same ID already exists.
        """
        if child.id in self.nodes_by_id:
            raise ValueError(f"Node with id {child.id} already exists")

        if self.root is None:
            self.root = parent

        parent.add_child(child)
        self.nodes.add(parent)
        self.nodes_by_id[parent.id] = parent

    def remove_node(self, node: DOMNode) -> None:
        """Remove a node from the DOM tree.

        Args:
            node: The node to remove. It will be disconnected from its parent
                  and removed from the tree's internal tracking structures.
        """
        if node in self.nodes:
            self.nodes.remove(node)
            self.nodes_by_id.pop(node.id, None)
            if node.parent:
                node.parent.remove_child(node)

    def get_node_list(self) -> list[DOMNode]:
        """Get a list of nodes in breadth-first tree order.

        Returns:
            A list of all nodes in the tree, ordered by breadth-first traversal.
            Returns an empty list if there is no root node.
        """
        if self.root is None:
            return []

        queue = deque([self.root])
        node_list = []

        while queue:
            current_node = queue.popleft()
            node_list.append(current_node)
            for child in current_node.children:
                queue.append(child)

        return node_list

    def get_tree_string(self, node: Optional[DOMNode] = None, indent: int = 0) -> str:
        """Get a string representation of the DOM tree for debugging.

        Args:
            node: The node to start from. If None, starts from the root.
            indent: The current indentation level for formatting.

        Returns:
            A formatted string representation of the tree structure,
            showing node names, IDs, dimensions, and positions.
        """
        if node is None:
            node = self.root
        if node is None:
            return ""

        node_width = node.widget.region.width if node.widget else "N/A"
        node_height = node.widget.region.height if node.widget else "N/A"
        node_x = node.widget.region.x if node.widget else "N/A"
        node_y = node.widget.region.y if node.widget else "N/A"

        lines = [
            " " * indent
            + f"{node.name} ({node.id}) ({node_width}x{node_height}) (Pos: {node_x}, {node_y})"
        ]
        for child in node.children:
            lines.append(self.get_tree_string(child, indent + 2))
        return "\n".join(line for line in lines if line)
