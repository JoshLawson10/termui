from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from termui.widgets._widget import Widget


@dataclass
class DOMNode:
    id: str
    name: Optional[str] = field(default_factory=str)
    widget: Optional["Widget"] = None
    parent: Optional["DOMNode"] = None
    children: list["DOMNode"] = field(default_factory=list)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"DOMNode(id={self.id!r}, children={len(self.children)})"

    def add_child(self, child: "DOMNode") -> None:
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "DOMNode") -> None:
        if child in self.children:
            child.parent = None
            self.children.remove(child)


class DOMTree:
    """A class representing a DOM tree for widgets."""

    def __init__(self):
        self.root: Optional[DOMNode] = None
        self.nodes: set[DOMNode] = set()
        self.nodes_by_id: dict[str, DOMNode] = {}

    def set_root(self, root: DOMNode) -> None:
        """Set the root of the DOM tree."""
        self.root = root
        self.nodes.add(root)
        self.nodes_by_id[root.id] = root

    def add_node(self, parent: DOMNode, child: DOMNode) -> None:
        """Add a node to the DOM tree."""
        if child.id in self.nodes_by_id:
            raise ValueError(f"Node with id {child.id} already exists")

        if self.root is None:
            self.root = parent

        parent.add_child(child)
        self.nodes.add(parent)
        self.nodes_by_id[parent.id] = parent

    def remove_node(self, node: DOMNode) -> None:
        """Remove a node from the DOM tree."""
        if node in self.nodes:
            self.nodes.remove(node)
            self.nodes_by_id.pop(node.id, None)
            if node.parent:
                node.parent.remove_child(node)

    def get_tree_string(self, node: Optional[DOMNode] = None, indent: int = 0) -> str:
        """Get a string representation of the DOM tree."""
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
            + f"{node.name} (Dimensions: {node_width}x{node_height}) (Pos: {node_x}, {node_y})"
        ]
        for child in node.children:
            lines.append(self.get_tree_string(child, indent + 2))
        return "\n".join(line for line in lines if line)
