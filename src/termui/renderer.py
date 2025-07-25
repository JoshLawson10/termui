import sys
from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod

from termui.colors import colorize
from termui.utils.geometry import Region
from termui.types.char import Char
from termui.cursor import Cursor as cursor
from termui.utils.terminal_utils import (
    get_terminal_size,
    clear_terminal,
)


@dataclass
class RenderNode:
    id: str
    region: Region
    content: list[list[Char]] = field(default_factory=list)
    z_index: int = 0
    visible: bool = True
    dirty: bool = True
    clip_to_parent: bool = True
    children: list["RenderNode"] = field(default_factory=list)
    parent: Optional["RenderNode"] = None

    def add_child(self, child: "RenderNode") -> None:
        """Add a child node to this render node."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "RenderNode") -> None:
        """Remove a child node from this render node."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def mark_dirty(self) -> None:
        """Mark this node as dirty."""
        self.dirty = True

    def mark_dirty_cascade_up(self) -> None:
        """Mark this node and all its ancestors as dirty."""
        self.mark_dirty()
        if self.parent:
            self.parent.mark_dirty_cascade_up()

    def get_absolute_region(self) -> Region:
        """Get the absolute region of this node in the terminal."""
        if self.parent is None:
            return self.region

        parent_region = self.parent.get_absolute_region()
        return Region(
            parent_region.x + self.region.x,
            parent_region.y + self.region.y,
            self.region.width,
            self.region.height,
        )

    def is_point_inside(self, x: int, y: int) -> bool:
        """Check if a point is inside this node's region."""
        return (
            self.region.x <= x < self.region.x + self.region.width
            and self.region.y <= y < self.region.y + self.region.height
        )


class Renderable(ABC):
    """Abstract base class for renderable objects."""

    @abstractmethod
    def get_render_node(self) -> RenderNode:
        """Get the render node for this object."""
        pass

    @abstractmethod
    def update_render_node(self, node: RenderNode) -> None:
        """Update the render node with the current state."""
        pass


class FrameBuffer:
    """A simple framebuffer to hold rendered content."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.current_frame: list[list[Char]] = [
            [Char(" ") for _ in range(width)] for _ in range(height)
        ]
        self.previous_frame: list[list[Char]] = [
            [Char(" ") for _ in range(width)] for _ in range(height)
        ]
        self.dirty_regions: set[tuple[int, int, int, int]] = (
            set()
        )  # (x, y, width, height)

    def resize(self, width: int, height: int) -> None:
        """Resize the framebuffer."""
        if width == self.width and height == self.height:
            return

        self.width = width
        self.height = height
        self.current_frame = [[Char(" ") for _ in range(width)] for _ in range(height)]
        self.previous_frame = [[Char(" ") for _ in range(width)] for _ in range(height)]
        self.mark_entire_screen_dirty()

    def mark_entire_screen_dirty(self) -> None:
        """Mark the entire screen as dirty."""
        self.dirty_regions.add((0, 0, self.width, self.height))

    def mark_region_dirty(self, region: Region) -> None:
        """Mark a specific region as dirty."""
        x = max(0, region.x)
        y = max(0, region.y)
        width = min(self.width - x, region.width)
        height = min(self.height - y, region.height)

        if width > 0 and height > 0:
            self.dirty_regions.add((x, y, width, height))

    def clear(self) -> None:
        """Clear the current frame."""
        self.current_frame = [
            [Char(" ") for _ in range(self.width)] for _ in range(self.height)
        ]
        self.mark_entire_screen_dirty()

    def draw_char(self, x: int, y: int, char: Char) -> None:
        """Draw a character at the specified position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.current_frame[y][x] != char:
                self.current_frame[y][x] = char
                self.mark_region_dirty(Region(x, y, 1, 1))

    def draw_content(
        self, region: Region, content: list[list[Char]], clip: bool = True
    ) -> None:
        """Draw a block of content at the specified position."""
        abs_x, abs_y = region.x, region.y

        for row_idx, row in enumerate(content):
            y = abs_y + row_idx
            if clip and (y < 0 or y >= self.height):
                continue

            for col_idx, char in enumerate(row):
                x = abs_x + col_idx
                if clip and (x < 0 or x >= self.width):
                    continue

                if 0 <= x < self.width and 0 <= y < self.height:
                    if self.current_frame[y][x] != char:
                        self.current_frame[y][x] = char

        self.mark_region_dirty(region)

    def render(self) -> None:
        """Render the current frame to the terminal."""
        if not self.dirty_regions:
            return

        for y in range(self.height):
            for x in range(self.width):
                current_char = self.current_frame[y][x]
                previous_char = self.previous_frame[y][x]

                if current_char != previous_char:
                    cursor.move(x + 1, y + 1)
                    sys.stdout.write(
                        colorize(
                            current_char.char,
                            fg=current_char.fg_color,
                            bg=current_char.bg_color,
                        )
                    )

        sys.stdout.flush()

        for y in range(self.height):
            for x in range(self.width):
                self.previous_frame[y][x] = self.current_frame[y][x]

        self.dirty_regions.clear()


class RenderTree:
    """A tree structure to manage render nodes."""

    def __init__(self):
        self.root = RenderNode("root", Region(0, 0, 1, 1))
        self.nodes: dict[str, RenderNode] = {"root": self.root}

    def add_node(self, node: RenderNode, parent_id: str = "root") -> None:
        """Add a node to the tree."""
        if node.id in self.nodes:
            raise ValueError(f"Node with id '{node.id}' already exists")

        parent = self.nodes.get(parent_id)
        if not parent:
            raise ValueError(f"Parent node '{parent_id}' not found")

        parent.add_child(node)
        self.nodes[node.id] = node

    def remove_node(self, node_id: str) -> None:
        """Remove a node from the tree."""
        node = self.nodes.get(node_id)
        if not node or node_id == "root":
            return

        if node.parent:
            node.parent.remove_child(node)

        self._remove_descendants(node)
        del self.nodes[node_id]

    def _remove_descendants(self, node: RenderNode) -> None:
        """Recursively remove all descendants of a node."""
        for child in list(node.children):
            self._remove_descendants(child)
            if child.id in self.nodes:
                del self.nodes[child.id]

    def get_node(self, node_id: str) -> Optional[RenderNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def traverse_visible_nodes(
        self, node: Optional[RenderNode] = None
    ) -> list[RenderNode]:
        """Traverse the tree and return all visible nodes in render order."""
        if node is None:
            node = self.root

        nodes = []
        if node.visible and node != self.root:
            nodes.append(node)

        sorted_children = sorted(node.children, key=lambda n: n.z_index)
        for child in sorted_children:
            nodes.extend(self.traverse_visible_nodes(child))

        return nodes

    def clear(self) -> None:
        """Clear the entire tree except root."""
        self.root.children.clear()
        self.nodes = {"root": self.root}


class Renderer:
    """The new main renderer class."""

    def __init__(self):
        self.width, self.height = get_terminal_size()
        self.frame_buffer = FrameBuffer(self.width, self.height)
        self.render_tree = RenderTree()
        self.renderables: dict[str, Renderable] = {}

        clear_terminal()
        cursor.hide()

    def resize_if_needed(self) -> None:
        """Check if terminal was resized and update accordingly."""
        new_width, new_height = get_terminal_size()
        if new_width != self.width or new_height != self.height:
            self.width = new_width
            self.height = new_height
            self.frame_buffer.resize(new_width, new_height)
            self.render_tree.root.region.width = new_width
            self.render_tree.root.region.height = new_height

    def register_renderable(
        self, renderable: Renderable, parent_id: str = "root"
    ) -> None:
        """Register a renderable object."""
        node = renderable.get_render_node()
        self.render_tree.add_node(node, parent_id)
        self.renderables[node.id] = renderable

    def unregister_renderable(self, renderable_id: str) -> None:
        """Unregister a renderable object."""
        self.render_tree.remove_node(renderable_id)
        if renderable_id in self.renderables:
            del self.renderables[renderable_id]

    def update_renderable(self, renderable_id: str) -> None:
        """Update a specific renderable."""
        renderable = self.renderables.get(renderable_id)
        node = self.render_tree.get_node(renderable_id)

        if renderable and node:
            renderable.update_render_node(node)
            node.mark_dirty()

    def render_frame(self) -> None:
        """Render a complete frame."""
        self.resize_if_needed()

        for node_id, renderable in self.renderables.items():
            node = self.render_tree.get_node(node_id)
            if node and node.dirty:
                renderable.update_render_node(node)

        self.frame_buffer.clear()

        visible_nodes = self.render_tree.traverse_visible_nodes()
        for node in visible_nodes:
            if node.dirty and node.content:
                abs_region = node.get_absolute_region()
                self.frame_buffer.draw_content(
                    abs_region, node.content, node.clip_to_parent
                )
                node.dirty = False

        self.frame_buffer.render()

    def clear(self) -> None:
        """Clear the renderer."""
        self.render_tree.clear()
        self.renderables.clear()
        self.frame_buffer.clear()

    def __del__(self):
        """Cleanup when renderer is destroyed."""
        cursor.show()
