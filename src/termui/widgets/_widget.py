import uuid
from abc import ABC, abstractmethod
from typing import Optional

from termui.dom import DOMNode
from termui.types.char import Char
from termui.utils.geometry import Region


class Widget(DOMNode, ABC):
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: Optional[str] = None, **kwargs) -> None:
        self.id = kwargs.get("id", str(uuid.uuid4()))
        self.name = name or f"Widget_{self.id[:8]}"
        super().__init__(id=self.id, name=self.name)

        self.region = Region(
            kwargs.get("x", 0),
            kwargs.get("y", 0),
            kwargs.get("width", 0),
            kwargs.get("height", 0),
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    def set_position(self, x: int, y: int) -> None:
        self.region.move_absolute(x, y)

    def set_size(self, width: int, height: int) -> None:
        self.region.update_dimensions(width, height)

    @abstractmethod
    def render(self) -> list[list[Char]]:
        """Render the widget."""
        pass
