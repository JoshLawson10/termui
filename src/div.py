from typing import Sequence


class Div:
    def __init__(
        self,
        name: str,
        column: int,
        column_end: int = 1,
        row: int = 1,
        row_end: int = 1,
        border: bool = False,
        border_color: str = "black",
        rounded_corners: bool = False,
        title: str = "",
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
    ) -> None:
        self.name: str = name
        self.column: int = column
        self.column_end: int = column_end
        self.row: int = row
        self.row_end: int = row_end
        self.border: bool = border
        self.border_color: str = border_color
        self.rounded_corners: bool = rounded_corners
        self.title: str = title
        self.padding: tuple[int, int, int, int] = padding
        self.content: list[list[str]] = []

    def __str__(self) -> str:
        return (
            f"Div(name={self.name}, "
            f"column={self.column}, "
            f"column_end={self.column_end}, "
            f"row={self.row}, "
            f"row_end={self.row_end}, "
            f"border={self.border}, "
            f"border_color={self.border_color}, "
            f"rounded_corners={self.rounded_corners}, "
            f"title={self.title}, "
            f"padding={self.padding})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def add_content(
        self, content: Sequence[Sequence[str]] | Sequence[str] | str
    ) -> None:
        """Add content to the div. Can accept:
        - A 2D list of strings (list[list[str]])
        - A single line of content (list[str])
        - A single text string (str)
        """
        if not self.content:
            self.content = []

        if isinstance(content, str):
            self.content.append([content])
        elif isinstance(content, list):
            if all(isinstance(item, str) for item in content):
                self.content.append([str(item) for item in content])
            elif all(
                isinstance(item, (list, tuple))
                and all(isinstance(subitem, str) for subitem in item)
                for item in content
            ):
                self.content.extend([list(item) for item in content])
            else:
                raise ValueError(
                    "Invalid content type - must be list[str] or list[list[str]]"
                )
        else:
            raise ValueError("Content must be str, list[str], or list[list[str]]")
