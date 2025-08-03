import sys
from typing import Optional

from termui.dom import DOMNode


class DuplicateIds(Exception):
    """Raised when attempting to add a widget with an id that already exists."""


class DOMTree:
    def __init__(self, root: Optional["DOMNode"] = None) -> None:
        self._root = root if root else DOMNode(id="root")
        self._nodes: list[DOMNode] = [self._root]
        self._nodes_set: set[DOMNode] = {self._root}
        self._nodes_by_id: dict[str, DOMNode] = {"root": self._root}

    def __bool__(self) -> bool:
        return bool(self._nodes)

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, child: object) -> bool:
        return child in self._nodes

    @property
    def root(self):
        return self._root

    def index(self, node: DOMNode, start: int = 0, stop: int = sys.maxsize):
        return self._nodes.index(node, start, stop)

    def _ensure_unique_id(self, widget_id: str) -> None:
        if widget_id in self._nodes_by_id:
            raise DuplicateIds(
                f"Tried to insert a widget with ID {widget_id!r}, but a widget already exists with that ID ({self._nodes_by_id[widget_id]!r}); "
                "ensure all child widgets have a unique ID."
            )

    def _append(self, node: DOMNode) -> None:
        if node not in self._nodes_set:
            self._nodes.append(node)
            self._nodes_set.add(node)
            node_id = node.id
            if node_id is not None:
                self._ensure_unique_id(node_id)
                self._nodes_by_id[node_id] = node

    def _insert(self, index: int, node: DOMNode) -> None:
        if node not in self._nodes_set:
            self._nodes.insert(index, node)
            self._nodes_set.add(node)
            node_id = node.id
            if node_id is not None:
                self._ensure_unique_id(node_id)
                self._nodes_by_id[node_id] = node

    def _remove(self, node: DOMNode) -> None:
        if node in self._nodes_set:
            del self._nodes[self._nodes.index(node)]
            self._nodes_set.remove(node)
            node_id = node.id
            if node_id in self._nodes_by_id:
                del self._nodes_by_id[node_id]

    def _clear(self) -> None:
        if self._nodes:
            self._nodes.clear()
            self._nodes_set.clear()
            self._nodes_by_id.clear()
