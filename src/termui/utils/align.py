from typing import Literal

type HorizontalAlignment = Literal["left", "center", "right"]
type VerticalAlignment = Literal["top", "middle", "bottom"]


def get_aligned_start_x(
    content: str, region_width: int, alignment: HorizontalAlignment
) -> int:
    """
    Calculate the starting x position for content alignment within a region.

    Args:
        content (str): The content to be aligned.
        region_width (int): The width of the region in which the content will be placed.
        alignment (HorizontalAlignment): The alignment type ('left', 'center', 'right').

    Returns:
        int: The starting x position for the content.
    """
    content_width = len(content)
    if alignment == "left":
        return 0
    elif alignment == "center":
        return (region_width - content_width) // 2
    elif alignment == "right":
        return region_width - content_width
    else:
        raise ValueError(f"Invalid alignment type: {alignment}")


def get_aligned_start_y(region_height: int, alignment: VerticalAlignment) -> int:
    """
    Calculate the starting y position for vertical alignment within a region.

    Args:
        region_height (int): The height of the region in which the content will be placed.
        alignment (VerticalAlignment): The alignment type ('top', 'middle', 'bottom').

    Returns:
        int: The starting y position for the content.
    """
    if alignment == "top":
        return 0
    elif alignment == "middle":
        return (region_height - 1) // 2
    elif alignment == "bottom":
        return region_height - 1
    else:
        raise ValueError(f"Invalid alignment type: {alignment}")
