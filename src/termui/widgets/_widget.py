import uuid
from abc import ABC, abstractmethod
from typing import Optional

from termui.char import Char
from termui.dom import DOMNode
from termui.events import MouseEvent
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

        self.pos: tuple[int | tuple[int, int], int | tuple[int, int]] = kwargs.get(
            "pos", (0, 0)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    def set_position(self, x: int, y: int) -> None:
        self.region.move_absolute(x, y)

    def set_size(self, width: int, height: int) -> None:
        self.region.update_dimensions(width, height)

    def get_minimum_size(self) -> tuple[int, int]:
        """Get the minimum size of the widget."""
        return 0, 0

    def handle_mouse_event(self, event: MouseEvent) -> None:
        if event.event_type == "press":
            self._on_click(event)
        else:
            self._on_mouse_enter()

    def _on_mouse_enter(self) -> None:
        """Handle mouse enter events."""
        pass

    def _on_mouse_exit(self) -> None:
        """Handle mouse exit events."""
        pass

    def _on_click(self, event: MouseEvent) -> None:
        """Handle mouse click events."""
        pass

    @abstractmethod
    def render(self) -> list[list[Char]]:
        """Render the widget."""
        pass
