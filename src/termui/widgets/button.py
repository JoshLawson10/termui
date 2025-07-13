from typing import Callable, Literal

from termui.widgets.widget import Widget

BORDER_CHARS: dict[
    str, tuple[tuple[str, str, str], tuple[str, str, str], tuple[str, str, str]]
] = {
    "ascii": (
        ("+", "-", "+"),
        ("|", " ", "|"),
        ("+", "-", "+"),
    ),
    "none": (
        (" ", " ", " "),
        (" ", " ", " "),
        (" ", " ", " "),
    ),
    "round": (
        ("╭", "─", "╮"),
        ("│", " ", "│"),
        ("╰", "─", "╯"),
    ),
    "solid": (
        ("┌", "─", "┐"),
        ("│", " ", "│"),
        ("└", "─", "┘"),
    ),
    "double": (
        ("╔", "═", "╗"),
        ("║", " ", "║"),
        ("╚", "═", "╝"),
    ),
    "dashed": (
        ("┏", "╍", "┓"),
        ("╏", " ", "╏"),
        ("┗", "╍", "┛"),
    ),
    "heavy": (
        ("┏", "━", "┓"),
        ("┃", " ", "┃"),
        ("┗", "━", "┛"),
    ),
    "thick": (
        ("█", "▀", "█"),
        ("█", " ", "█"),
        ("█", "▄", "█"),
    ),
    "hkey": (
        ("▔", "▔", "▔"),
        (" ", " ", " "),
        ("▁", "▁", "▁"),
    ),
    "vkey": (
        ("▏", " ", "▕"),
        ("▏", " ", "▕"),
        ("▏", " ", "▕"),
    ),
}

BorderStyle = Literal[
    "ascii",
    "none",
    "round",
    "solid",
    "double",
    "dashed",
    "heavy",
    "thick",
    "hkey",
    "vkey",
]


class Button(Widget):
    """A simple button widget that can be clicked.

    Parameters
    ----------
    label : str
        The text displayed on the button.
    variant : ButtonVariant, optional
        The visual style of the button, by default "default".
    style : ButtonStyle, optional
        The button style, by default "solid".
    name : str, optional
        The name of the button, by default None.
    on_click : Callable[[str], None]
        The callback function to be called when the button is clicked.
    disabled : bool, optional
        Whether the button is disabled, by default False.
    padding : tuple[int, int, int, int], optional
        Padding around the button content, by default (0, 0, 0, 0).
    """

    def __init__(
        self,
        label: str,
        *,
        border: BorderStyle = "solid",
        name: str | None = None,
        on_click: Callable,
        disabled: bool = False,
        padding: tuple[int, int, int, int] = (0, 0, 0, 0),
    ) -> None:
        """Initialize a Button widget."""
        super().__init__(
            name=name if name else f"Button {label}",
        )
        if not callable(on_click):
            raise TypeError("on_click must be a callable function.")
        self.name = name if name else f"Button {label}"
        self.label = label
        self.border = border
        self.width = len(label) + padding[1] + padding[3] + 2
        self.height = 3 + padding[0] + padding[2]
        self.on_click = on_click
        self.disabled = disabled
        self.padding = padding

        self._state: Literal["default", "selected", "pressed"] = "default"

    def render(self) -> list[list[str]]:
        """Render the button."""
        self.width = len(self.label) + self.padding[1] + self.padding[3] + 2
        self.height = 3 + self.padding[0] + self.padding[2]

        border_chars = BORDER_CHARS.get(self.border, BORDER_CHARS["solid"])
        tl, tr, bl, br = (
            border_chars[0][0],
            border_chars[0][2],
            border_chars[2][0],
            border_chars[2][2],
        )
        v, h = border_chars[1][0], border_chars[0][1]
        content: list[list[str]] = [[tl] + [h] * (self.width - 2) + [tr]]

        for _ in range(self.padding[0]):
            content.append([" "] * self.width)

        label_line: list[str] = (
            [" "] * self.padding[3]
            + list(self.label)
            + [" "] * (self.width - len(self.label) - self.padding[3] - 2)
        )
        content.append([v] + label_line + [v])

        for _ in range(self.padding[2]):
            content.append([" "] * self.width)

        content.append([bl] + [h] * (self.width - 2) + [br])

        return content

    def click(self) -> None:
        """Simulate a button click."""
        if self.disabled:
            return
        self.on_click()

    """A widget that represents a button."""
