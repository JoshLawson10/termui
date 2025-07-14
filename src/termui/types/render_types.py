from dataclasses import dataclass

from termui.geometry import Region
from termui.widgets._widget import Widget


@dataclass
class RenderedObject:
    """A class representing a rendered object in the TermUI framework."""

    widget: Widget
    region: Region
    index: int
    dirty: bool = True
