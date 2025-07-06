from typing import Sequence, Literal
from functools import singledispatch


class Div:
    """A Div represents a rectangular area on the screen with optional borders and titles.

    Parameters
    ----------
    name (str)
        The name of the div.
    column (int)
        The starting column of the div (1-indexed).
    column_end (int)
        The ending column of the div (1-indexed, default is 1).
    row (int)
        The starting row of the div (1-indexed).
    row_end (int)
        The ending row of the div (1-indexed, default is 1).
    border (bool)
        Whether the div has a border (default is False).
    rounded_corners (bool)
        Whether the div has rounded corners (default is False).
    title (str)
        The title of the div (default is an empty string).
    title_align (Literal["left", "center", "right"])
        The alignment of the title within the div (default is "left").
        Valid values are "left", "center", and "right".
    padding (tuple[int, int, int, int])
        Padding around the content of the div in the order (top, right, bottom, left) (default is (0, 0, 0, 0)).
    """

    def __init__(
        self,
        name: str,
        start_col: int,
        end_col: int = 1,
        start_row: int = 1,
        end_row: int = 1,
        border: bool = False,
        rounded_corners: bool = False,
        title: str = "",
        title_align: Literal["left", "center", "right"] = "left",
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
    ) -> None:
        self.name: str = name
        self.start_col: int = start_col
        self.end_col: int = end_col
        self.start_row: int = start_row
        self.end_row: int = end_row
        self.border: bool = border
        self.rounded_corners: bool = rounded_corners
        self.title: str = title
        self.title_align: Literal["left", "center", "right"] = title_align
        self.padding: tuple[int, int, int, int] = padding
        self.content: list[list[str]] = []

    def __str__(self) -> str:
        return (
            f"Div(name={self.name}, "
            f"start_col={self.start_col}, "
            f"end_col={self.end_col}, "
            f"start_row={self.start_row}, "
            f"end_row={self.end_row}, "
            f"border={self.border}, "
            f"rounded_corners={self.rounded_corners}, "
            f"title={self.title}, "
            f"title_align={self.title_align}, "
            f"padding={self.padding})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    @singledispatch
    def add_content(self, content: str) -> None:
        """Add content to the div.

        Parameters
        ----------
        content: str
            The content to add to the div.
        """
        if not self.content:
            self.content = []
        self.content.append([content])

    @add_content.register(list[str])
    def _(self, content: list[str]) -> None:
        """Add a list of strings as content to the div.

        Parameters
        ----------
        content: list[str]
            A list of strings to add as content to the div.
        """
        if not self.content:
            self.content = []
        for line in content:
            self.content.append(list(line))

    @add_content.register(list[list[str]])
    def _(self, content: list[list[str]]) -> None:
        """Add a 2D list of strings as content to the div.

        Parameters
        ----------
        content: list[list[str]]
            A 2D list of strings to add as content to the div.
        """
        if not self.content:
            self.content = []
        for line in content:
            self.content.append(list(line))

    def render(self, width: int, height: int) -> list[list[str]]:
        """Render the div as a 2D list of strings.

        Parameters
        ----------
        width : int
            The width of the Div in characters.
        height : int
            The height of the Div in characters.

        Returns
        -------
        list[list[str]]
            A 2D list of strings representing the rendered Div.
        """
        rendered: list[list[str]] = []

        ptop, pright, pbottom, pleft = self.padding
        content_width: int = max(0, width - pleft - pright - (2 if self.border else 0))
        content_height: int = max(
            0, height - ptop - pbottom - (2 if self.border else 0)
        )

        content_lines: list[list[str]] = []
        for _ in range(content_height):
            content_lines.append([" "] * content_width)

        for i, line in enumerate(self.content):
            if i >= content_height:
                break
            for j, char in enumerate(line):
                if j >= content_width:
                    break
                content_lines[i][j] = char

        if not self.border:
            rendered = content_lines
        else:
            rendered = []

            if self.rounded_corners:
                tl, tr, bl, br = "╭", "╮", "╰", "╯"
            else:
                tl, tr, bl, br = "┌", "┐", "└", "┘"
            h, v = "─", "│"

        top_border: list[str] = [tl] + [h] * (width - 2) + [tr]
        if self.title:
            title: str = f" {self.title} "
            if len(title) <= width - 2:
                match self.title_align:
                    case "left":
                        start_pos: int = 1
                    case "center":
                        start_pos: int = (width - len(title)) // 2
                    case "right":
                        start_pos: int = width - len(title) - 1
                    case _:
                        raise ValueError("Invalid title alignment specified.")
                end_pos: int = start_pos + len(title)
                top_border[start_pos:end_pos] = list(title)
        rendered.append(top_border)

        for _ in range(height - 2):
            row: list[str] = [v] + [" "] * (width - 2) + [v]
            rendered.append(row)

        rendered.append([bl] + [h] * (width - 2) + [br])

        content_start_row: int = 1 + ptop
        content_start_col: int = 1 + pleft
        for i, line in enumerate(content_lines):
            if content_start_row + i >= len(rendered) - 1:
                break
            for j, char in enumerate(line):
                if content_start_col + j >= len(rendered[0]) - 1:
                    break
                rendered[content_start_row + i][content_start_col + j] = char

        return rendered
