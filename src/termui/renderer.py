from dataclasses import dataclass
import sys

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

    def _print_text_at_position(self, text: str, x: int, y: int) -> None:
        """Print text at a specific position in the terminal."""
        move_cursor_to(x, y)
        sys.stdout.write(text)
        sys.stdout.flush()

    def render(self) -> None:
        """Render all widgets."""
        for rendered_object in self.widgets:
            pre_render: list[str] = rendered_object.widget.render()
            for i, line in enumerate(pre_render):
                self._print_text_at_position(
                    line, rendered_object.region.x, rendered_object.region.y + i
                )
