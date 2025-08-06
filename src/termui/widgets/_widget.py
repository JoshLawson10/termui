import uuid
from abc import ABC, abstractmethod
from typing import Optional, Union

from termui.dom import DOMNode
from termui.types.char import Char
from termui.utils.geometry import Region


class Widget(DOMNode, ABC):
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: Optional[str] = None, **kwargs) -> None:
        self.id = kwargs.get("id", str(uuid.uuid4()))
        self.name = name or f"Widget_{self.id[:8]}"
        super().__init__(id=self.id, name=self.name, widget=self)

        self.region = Region(
            kwargs.get("x", 0),
            kwargs.get("y", 0),
            kwargs.get("width", 0),
            kwargs.get("height", 0),
        )

        self.row: int | tuple[int, int] = kwargs.get("row", 0)
        self.col: int | tuple[int, int] = kwargs.get("col", 0)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    def set_position(self, x: int, y: int) -> None:
        self.region.move_absolute(x, y)

    def set_size(self, width: int, height: int) -> None:
        self.region.update_dimensions(width, height)

    def get_minimum_size(self) -> tuple[int, int]:
        """Get the minimum size of the widget."""
        return 0, 0

    @abstractmethod
    def render(self) -> list[list[Char]]:
        """Render the widget."""
        pass
