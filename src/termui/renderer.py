from dataclasses import dataclass

from termui.widgets.base import Widget
from termui.geometry import Region
from termui.render_geometry import RenderedObject
from termui.utils import move_cursor_to


class Renderer:
    def __init__(self) -> None:
        self.widgets: list[RenderedObject] = []

    def pipe(self, widget: Widget, x: int, y: int, index: int = 1) -> None:
        """Add a rendered object to the renderer."""
        region = Region(x, y, widget.width, widget.height)
        rendered_object = RenderedObject(widget=widget, region=region, index=index)
        self.widgets.append(rendered_object)

    def render(self) -> None:
        """Render all widgets."""
        for rendered_object in self.widgets:
            move_cursor_to(rendered_object.region.x, rendered_object.region.y)
            print(
                f"Rendering {rendered_object.widget.name} at {rendered_object.region}"
            )
