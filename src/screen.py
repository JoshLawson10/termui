import os
from div import Div


class Screen:
    def __init__(self, width: int, height: int, cols: int, rows: int) -> None:
        self.width: int = width if width > 0 else os.get_terminal_size().columns
        self.height: int = height if height > 0 else os.get_terminal_size().lines
        self.cell_width: int = self.width // cols if cols > 0 else 1
        self.cell_height: int = self.height // rows if rows > 0 else 1
        self.divs: list[Div] = []

    def __str__(self) -> str:
        return f"Screen(width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        return self.__str__()

    def add(self, div: Div) -> None:
        """Add a Div to the screen."""
        if not isinstance(div, Div):
            raise TypeError("Expected a Div instance.")
        self.divs.append(div)

    def remove(self, div: Div) -> None:
        """Remove a Div from the screen."""
        if div in self.divs:
            self.divs.remove(div)

    def setup(self) -> None:
        """Setup the screen with initial Divs.

        From within :meth:`Screen.setup`, you can add Divs to the screen
        by calling :meth:`Screen.add`, and remove them by calling :meth:`Screen.remove`.
        All Divs currently on the screen will be stored in the :attr:`Screen.divs` list.
        """
        pass


class Login(Screen):
    def setup(self) -> None:
        """Setup the login screen with a Div."""
        login_div = Div(
            name="login",
            column=1,
            column_end=3,
            row=1,
            row_end=3,
            border=True,
            border_color="blue",
            rounded_corners=True,
            title="Login",
            padding=(1, 1, 1, 1),
        )
        self.add(login_div)
