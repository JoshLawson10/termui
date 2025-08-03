from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from termui.widgets._widget import Widget


@dataclass
class DOMNode:
    id: str
    widget: Widget = field(default_factory=Widget)
    parent: Optional["DOMNode"] = None
    children: list["DOMNode"] = field(default_factory=list)

    def __hash__(self):
        return hash(self.id)

    def add_child(self, child: "DOMNode") -> None:
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "DOMNode"):
        if child in self.children:
            child.parent = None
            self.children.remove(child)
