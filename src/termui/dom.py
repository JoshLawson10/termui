from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from termui.screen import Screen
    from termui.widgets._widget import Widget


class NoScreen(Exception):
    """Exception raised when a DOMNode is not associated with a Screen."""


@dataclass
class DOMNode:
    id: str
    widget: Widget = field(default_factory=Widget)
    parent: Optional["DOMNode"] = None
    children: list["DOMNode"] = field(default_factory=list)

    def __hash__(self):
        return hash(self.id)

    @property
    def screen(self) -> "Screen":
        from termui.screen import Screen

        node = self
        try:
            while node is not None and not isinstance(node, Screen):
                node = node.parent
        except AttributeError:
            raise RuntimeError(
                "Widget is missing attributes; have you called the constructor in your widget class?"
            ) from None
        if not isinstance(node, Screen):
            raise NoScreen("node has no screen")
        return node

    def add_child(self, child: "DOMNode") -> None:
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "DOMNode"):
        if child in self.children:
            child.parent = None
            self.children.remove(child)
