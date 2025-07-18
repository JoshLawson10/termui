from abc import ABC, abstractmethod
from dataclasses import dataclass


from termui.utils.geometry import Region
from termui.widgets._widget import Widget

type Object = "Widget | Layout"


@dataclass
class Placement:
    """A class representing the placement of a widget on a screen."""

    child: Object
    region: Region


class Layout(ABC):
    """An abstract base class for layouts."""

    def __init__(self, *children: Object) -> None:
        self.children: list[Object] = list(children)
        self.placements: list[Placement] = []
        self.width: int = 0
        self.height: int = 0

    def update_dimensions(self, width: int, height: int) -> None:
        """Update the layout's dimensions based on its children."""
        self.width = width
        self.height = height

    def add_placement(
        self, child: Object, x_pos: int, y_pos: int, width: int, height: int
    ) -> None:
        """Add a placement for a widget."""
        region = Region(x_pos, y_pos, width, height)
        self.placements.append(Placement(child=child, region=region))

    @abstractmethod
    def arrange(self) -> None:
        """Arrange the widgets on the screen.

        This method should be implemented by subclasses to define how widgets are placed.
        """
        pass
