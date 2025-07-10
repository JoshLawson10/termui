from typing import Literal, Optional
from termui.colors import colorize, AnsiColor


class Div:
    """A Div represents a rectangular area on the screen with optional borders and titles.

    Parameters
    ----------
    name (str)
        The name of the div.
    start_col (int)
        The starting column of the div (1-indexed).
    end_col (int)
        The ending column of the div (1-indexed, default is 1).
    start_row (int)
        The starting row of the div (1-indexed).
    end_row (int)
        The ending row of the div (1-indexed, default is 1).
    border (bool)
        Whether the div has a border (default is False).
    rounded_corners (bool)
        Whether the div has rounded corners (default is False).
    title (str)
        The title of the div (default is an empty string).
    align_title (Literal["left", "center", "right"])
        The alignment of the title within the div (default is "left").
        Valid values are "left", "center", and "right".
    horizontal_align (Literal["left", "center", "right"])
        The alignment of the content within the div (default is "left").
        Valid values are "left", "center", and "right".
    vertical_align (Literal["top", "center", "bottom"])
        The vertical alignment of the content within the div (default is "top").
        Valid values are "top", "center", and "bottom".
    padding (tuple[int, int, int, int])
        Padding around the content of the div in the order (top, right, bottom, left) (default is (0, 0, 0, 0)).
    fg_color (Optional[Color])
        Foreground color of the div (default is None).
    bg_color (Optional[Color])
        Background color of the div (default is None).
    border_fg_color (Optional[Color])
        Foreground color of the border (default is None).
    border_bg_color (Optional[Color])
        Background color of the border (default is None).
    title_fg_color (Optional[Color])
        Foreground color of the title (default is None).
    title_bg_color (Optional[Color])
        Background color of the title (default is None).
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
        align_title: Literal["left", "center", "right"] = "left",
        horizontal_align: Literal["left", "center", "right"] = "left",
        vertical_align: Literal["top", "center", "bottom"] = "top",
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
        fg_color: Optional[AnsiColor] = None,
        bg_color: Optional[AnsiColor] = None,
        border_fg_color: Optional[AnsiColor] = None,
        border_bg_color: Optional[AnsiColor] = None,
        title_fg_color: Optional[AnsiColor] = None,
        title_bg_color: Optional[AnsiColor] = None,
    ) -> None:
        self.name: str = name
        self.start_col: int = start_col
        self.end_col: int = end_col
        self.start_row: int = start_row
        self.end_row: int = end_row
        self.border: bool = border
        self.rounded_corners: bool = rounded_corners
        self.title: str = title
        self.align_title: Literal["left", "center", "right"] = align_title
        self.horizontal_align: Literal["left", "center", "right"] = horizontal_align
        self.vertical_align: Literal["top", "center", "bottom"] = vertical_align
        self.padding: tuple[int, int, int, int] = padding
        self.fg_color: Optional[AnsiColor] = fg_color
        self.bg_color: Optional[AnsiColor] = bg_color
        self.border_fg_color: Optional[AnsiColor] = border_fg_color
        self.border_bg_color: Optional[AnsiColor] = border_bg_color
        self.title_fg_color: Optional[AnsiColor] = title_fg_color
        self.title_bg_color: Optional[AnsiColor] = title_bg_color
        self._styled_content: list[
            list[tuple[str, Optional[AnsiColor], Optional[AnsiColor]]]
        ] = []

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
            f"horizontal_align={self.horizontal_align}, "
            f"vertical_align={self.vertical_align}, "
            f"padding={self.padding}), "
            f"fg_color={self.fg_color}, "
            f"bg_color={self.bg_color}, "
            f"border_fg_color={self.border_fg_color}, "
            f"border_bg_color={self.border_bg_color}, "
            f"title_fg_color={self.title_fg_color}, "
            f"title_bg_color={self.title_bg_color}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def set_content(
        self,
        content: (
            str
            | list[str]
            | list[list[str]]
            | list[list[tuple[str, Optional[AnsiColor], Optional[AnsiColor]]]]
        ),
        fg_color: Optional[AnsiColor] = None,
        bg_color: Optional[AnsiColor] = None,
    ) -> None:
        """Set the content of the Div.

        Parameters
        ----------
        content : str | list[str] | list[list[str]] | list[list[tuple[str, Optional[AnsiColor], Optional[AnsiColor]]]]
            The content to set. It can be:
            - A single string
            - A list of strings (each string is a line)
            - A list of lists of strings (each inner list is a line with multiple items)
            - A list of lists of tuples (pre-styled content with (text, fg_color, bg_color))
        fg_color : Optional[Color]
            Default foreground color for unstyled content
        bg_color : Optional[Color]
            Default background color for unstyled content
        """
        self._styled_content = []

        if isinstance(content, str):
            lines = [content]
        else:
            lines = content

        for line in lines:
            styled_line = []
            if isinstance(line, str):
                styled_line.append(
                    (line, fg_color or self.fg_color, bg_color or self.bg_color)
                )
            else:
                for item in line:
                    if isinstance(item, tuple):
                        styled_line.append(item)
                    else:
                        styled_line.append(
                            (item, fg_color or self.fg_color, bg_color or self.bg_color)
                        )
            self._styled_content.append(styled_line)

    def _apply_style(
        self, char: str, is_border: bool = False, is_title: bool = False
    ) -> str:
        if is_title:
            return colorize(char, fg=self.title_fg_color, bg=self.title_bg_color)
        elif is_border:
            return colorize(char, fg=self.border_fg_color, bg=self.border_bg_color)
        return colorize(char, fg=self.fg_color, bg=self.bg_color)

    def _align_content(
        self,
        content: list[str],
        width: int,
        align: Literal["left", "center", "right"],
    ) -> list[str]:
        aligned: list[str] = []
        for line in content:
            match align:
                case "left":
                    aligned.append(line.ljust(width))
                case "center":
                    aligned.append(line.center(width))
                case "right":
                    aligned.append(line.rjust(width))
                case _:
                    raise ValueError(f"Invalid alignment specified: {align}")
        return aligned

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
        if width <= 0 or height <= 0:
            return []

        ptop, pright, pbottom, pleft = self.padding

        content_width = max(0, width - pleft - pright - (2 if self.border else 0))

        content_lines = []
        for styled_line in self._styled_content:
            line = "".join([item[0] for item in styled_line])
            content_lines.append(line)

        aligned_content = []
        for line in content_lines:
            if self.horizontal_align == "left":
                aligned = line.ljust(content_width)[:content_width]
            elif self.horizontal_align == "center":
                aligned = line.center(content_width)[:content_width]
            elif self.horizontal_align == "right":
                aligned = line.rjust(content_width)[:content_width]
            else:
                aligned = line.ljust(content_width)[:content_width]
            aligned_content.append(aligned)

        rendered: list[list[str]] = [[" " for _ in range(width)] for _ in range(height)]

        if not self.border:
            if self.vertical_align == "top":
                start_y: int = ptop
            elif self.vertical_align == "center":
                start_y: int = max(0, (height - len(aligned_content)) // 2)
            elif self.vertical_align == "bottom":
                start_y: int = max(0, height - len(aligned_content) - pbottom)
            else:
                start_y: int = ptop

            for i, line in enumerate(aligned_content):
                y_pos: int = start_y + i
                if 0 <= y_pos < height:
                    for j, char in enumerate(line):
                        x_pos: int = pleft + j
                        if 0 <= x_pos < width:
                            if i < len(self._styled_content) and j < len(
                                self._styled_content[i]
                            ):
                                _, fg, bg = self._styled_content[i][j]
                            else:
                                fg, bg = self.fg_color, self.bg_color
                            rendered[y_pos][x_pos] = colorize(char, fg=fg, bg=bg)
        else:
            if self.rounded_corners:
                tl, tr, bl, br = "╭", "╮", "╰", "╯"
            else:
                tl, tr, bl, br = "┌", "┐", "└", "┘"
            h, v = "─", "│"

            for y in range(height):
                for x in range(width):
                    if y == 0 and x == 0:
                        rendered[y][x] = self._apply_style(tl, is_border=True)
                    elif y == 0 and x == width - 1:
                        rendered[y][x] = self._apply_style(tr, is_border=True)
                    elif y == height - 1 and x == 0:
                        rendered[y][x] = self._apply_style(bl, is_border=True)
                    elif y == height - 1 and x == width - 1:
                        rendered[y][x] = self._apply_style(br, is_border=True)
                    elif y == 0 or y == height - 1:
                        rendered[y][x] = self._apply_style(h, is_border=True)
                    elif x == 0 or x == width - 1:
                        rendered[y][x] = self._apply_style(v, is_border=True)

            if self.title and height > 0:
                title: str = f" {self.title} "
                if len(title) <= width - 2:
                    if self.align_title == "left":
                        start_x: int = 1
                    elif self.align_title == "center":
                        start_x: int = (width - len(title)) // 2
                    elif self.align_title == "right":
                        start_x: int = width - len(title) - 1
                    else:
                        start_x: int = 1

                    for i, char in enumerate(title):
                        x_pos = start_x + i
                        if 1 <= x_pos < width - 1:
                            rendered[0][x_pos] = self._apply_style(char, is_title=True)

            if self.vertical_align == "top":
                start_y: int = ptop + 1
            elif self.vertical_align == "center":
                start_y: int = max(1, (height - len(aligned_content)) // 2)
            elif self.vertical_align == "bottom":
                start_y: int = max(1, height - len(aligned_content) - pbottom - 1)
            else:
                start_y: int = ptop + 1

            for i, line in enumerate(aligned_content):
                y_pos: int = start_y + i
                if 1 <= y_pos < height - 1:
                    line_length: int = len(line)
                    if self.horizontal_align == "left":
                        start_x: int = pleft + 1
                    elif self.horizontal_align == "center":
                        start_x: int = max(1, (width - line_length) // 2)
                    elif self.horizontal_align == "right":
                        start_x: int = max(1, width - line_length - pright - 1)
                    else:
                        start_x: int = pleft + 1

                    for j, char in enumerate(line):
                        x_pos: int = start_x + j
                        if 1 <= x_pos < width - 1:
                            if i < len(self._styled_content) and j < len(
                                self._styled_content[i]
                            ):
                                _, fg, bg = self._styled_content[i][j]
                            else:
                                fg, bg = self.fg_color, self.bg_color
                            rendered[y_pos][x_pos] = colorize(char, fg=fg, bg=bg)

        return rendered
