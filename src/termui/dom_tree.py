from collections import deque
from typing import Optional, cast

from termui.dom_node import DOMNode
from termui.layout import Layout
from termui.widget import Widget
from termui.widgets import Container


class DOMTree:
    """A DOM tree for managing widget hierarchies and rendering order.

    The DOMTree maintains a hierarchical structure of widgets and provides
    methods for traversal, manipulation, and debugging.
    """

    def __init__(self) -> None:
        """Initialize an empty DOM tree."""
        self.root: Optional[DOMNode] = None
        """The root node of the DOM tree."""
        self.nodes: set[DOMNode] = set()
        """A set of all nodes in the DOM tree. Used for quick lookups."""
        self.nodes_by_id: dict[str, DOMNode] = {}
        """A dictionary mapping node IDs to their corresponding DOM nodes."""
        self.nodes_by_name: dict[str, DOMNode] = {}
        """A dictionary mapping node names to their corresponding DOM nodes."""
        self._layout_dirty = False
        """Whether the layout needs to be recalculated."""

    def set_root(self, root: DOMNode) -> None:
        """Set the root of the DOM tree.

        Args:
            root: The node to set as the root of the tree.
        """
        self.root = root
        self._add_node_to_lookups(root)

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
            self._add_node_to_lookups(parent)

        parent.add_child(child)
        self._add_node_to_lookups(child)

    def _add_node_to_lookups(self, node: DOMNode) -> None:
        """Add a node to all tracking structures.

        Args:
            node: The node to add to the tracking structures.
        """
        self.nodes.add(node)
        self.nodes_by_id[node.id] = node

        # Use name if available, otherwise fall back to ID
        name_key = node.name if node.name else node.id
        self.nodes_by_name[name_key] = node

        for child in node.children:
            self._add_node_to_lookups(child)

    def remove_node(self, node: DOMNode) -> None:
        """Remove a node from the DOM tree.

        Args:
            node: The node to remove. It will be disconnected from its parent
                  and removed from the tree's internal tracking structures.
        """
        if node in self.nodes:
            self.nodes.remove(node)
            self.nodes_by_id.pop(node.id, None)

            # Remove from nodes_by_name using the same key logic
            name_key = node.name if node.name else node.id
            self.nodes_by_name.pop(name_key, None)

            if node.parent:
                node.parent.remove_child(node)

    def get_node_by_id(self, node_id: str) -> Optional[DOMNode]:
        """Get a node by its ID.

        Args:
            node_id: The ID of the node to find.

        Returns:
            The DOMNode with the matching ID, or None if not found.
        """
        return self.nodes_by_id.get(node_id)

    def get_node_by_name(self, name: str) -> Optional[DOMNode]:
        """Get a node by its name.

        Args:
            name: The name of the widget to find.

        Returns:
            The DOMNode with the matching name, or None if not found.
        """
        return self.nodes_by_name.get(name)

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

    def get_node_at_coordinate(self, x: int, y: int) -> Optional[DOMNode]:
        """Get a node at the specified position.

        Args:
            x: The x-coordinate to check.
            y: The y-coordinate to check.

        Returns:
            The DOMNode at the specified position, or None if not found.
        """
        for node in self.get_node_list():
            if isinstance(node, Widget) and node.region.contains(x, y):
                return node
        return None

    def get_widget_at_coordinate(self, x: int, y: int) -> Optional["Widget"]:
        """Get a widget at the specified position.

        Note: Will never return a layout or container object, always a standalone widget.

        Args:
            x: The x-coordinate to check.
            y: The y-coordinate to check.

        Returns:
            The Widget at the specified position, or None if not found.
        """
        for node in self.get_node_list():
            if (
                isinstance(node, Widget)
                and node.region.contains(x, y)
                and not isinstance(node, Layout)
                and not isinstance(node, Container)
            ):
                return node
        return None

    def get_tree_string(self, node: Optional[DOMNode] = None, indent: int = 0) -> str:
        """Get a string representation of the DOM tree for debugging.

        Args:
            node: The node to start from. If None, starts from the root.
            indent: The current indentation level for formatting.

        Returns:
            A formatted string representation of the tree structure,
            showing node names, IDs, dimensions, and positions.
        """
        if node is None and self.root is None:
            return "<empty tree>"

        if node is None:
            node = self.root

        if not isinstance(node, Widget):
            return "<non-widget node>"

        node = cast(Widget, node)

        node_width = node.region.width
        node_height = node.region.height
        node_x = node.region.x
        node_y = node.region.y

        lines = [
            " " * indent
            + f"{node.name} ({node.id}) ({node_width}x{node_height}) (Coords: {node_x}, {node_y})"
        ]
        for child in node.children:
            lines.append(self.get_tree_string(child, indent + 2))
        return "\n".join(line for line in lines if line)

    def arrange_all_widgets(self) -> None:
        """Arrange all widgets using BFS traversal."""
        if not self._layout_dirty or not self.root:
            return

        queue = deque([self.root])

        while queue:
            current = queue.popleft()

            if isinstance(current, Layout):
                current.arrange()

            for child in current.children:
                queue.append(child)

        self._layout_dirty = False

    def mark_layout_dirty(self) -> None:
        """Mark the entire layout as needing recalculation."""
        self._layout_dirty = True

    def mark_subtree_dirty(self, node: DOMNode) -> None:
        """Mark a subtree as needing layout recalculation.

        Args:
            node: The root node of the subtree to mark as dirty.
        """
        self._layout_dirty = True
        node.mark_dirty_cascade_down()
