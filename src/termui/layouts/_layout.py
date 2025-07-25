from abc import ABC, abstractmethod
from typing import Literal, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from termui.widgets._base_container import BaseContainerWidget
    from termui.widgets._widget import Widget


@dataclass
class LayoutConstraints:
    """Base class for layout constraints."""

    min_width: int = 0
    min_height: int = 0
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    preferred_width: Optional[int] = None
    preferred_height: Optional[int] = None
    flex_grow: float = 0.0  # How much to grow when extra space is available
    flex_shrink: float = 1.0  # How much to shrink when space is limited


class LayoutManager(ABC):
    """Base class for layout managers."""

    @abstractmethod
    def layout(
        self, container: "BaseContainerWidget", children: list["Widget"]
    ) -> None:
        """Layout the children within the container."""
        pass


class BoxLayoutManager(LayoutManager):
    """Base class for box-based layouts."""

    def __init__(
        self,
        direction: Literal["horizontal", "vertical"],
        gap: int = 0,
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
    ):
        self.direction = direction
        self.gap = gap
        self.padding = padding  # top, right, bottom, left

    def layout(
        self, container: "BaseContainerWidget", children: list["Widget"]
    ) -> None:
        """Layout children in a box layout."""
        if not children:
            return

        padding_top, padding_right, padding_bottom, padding_left = self.padding
        available_width = container.width - padding_left - padding_right
        available_height = container.height - padding_top - padding_bottom

        if self.direction == "horizontal":
            self._layout_horizontal(
                children, available_width, available_height, padding_left, padding_top
            )
        else:
            self._layout_vertical(
                children, available_width, available_height, padding_left, padding_top
            )

    def _layout_horizontal(
        self,
        children: list["Widget"],
        available_width: int,
        available_height: int,
        start_x: int,
        start_y: int,
    ) -> None:
        """Layout children horizontally."""
        total_gap = self.gap * (len(children) - 1) if len(children) > 1 else 0

        remaining_width = available_width - total_gap
        current_x = start_x

        child_width = remaining_width // len(children) if children else 0
        extra_width = remaining_width % len(children) if children else 0

        for i, child in enumerate(children):
            width = child_width + (1 if i < extra_width else 0)
            height = available_height

            child.set_bounds(current_x, start_y, width, height)
            current_x += width + self.gap

    def _layout_vertical(
        self,
        children: list["Widget"],
        available_width: int,
        available_height: int,
        start_x: int,
        start_y: int,
    ) -> None:
        """Layout children vertically."""
        total_gap = self.gap * (len(children) - 1) if len(children) > 1 else 0

        remaining_height = available_height - total_gap
        current_y = start_y

        child_height = remaining_height // len(children) if children else 0
        extra_height = remaining_height % len(children) if children else 0

        for i, child in enumerate(children):
            width = available_width
            height = child_height + (1 if i < extra_height else 0)

            child.set_bounds(start_x, current_y, width, height)
            current_y += height + self.gap
