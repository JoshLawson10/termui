from abc import ABC, abstractmethod
from typing import Literal

"""Defines the way widget sizing is to behave"""
type SizingPolicy = Literal["fixed", "grow", "shrink"]


class Widget(ABC):
    """Base class for all widgets in the TermUI framework."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.width: int = 0
        self.height: int = 0
        self.sizing_policy: SizingPolicy = "fixed"

    def update_dimensions(self, width: int, height: int) -> None:
        """Update the dimensions of the widget."""
        self.width = width
        self.height = height

    @abstractmethod
    def render(self) -> list[list[str]]:
        """Render the widget."""
        pass
