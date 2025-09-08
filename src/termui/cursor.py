from termui._context_manager import app


class Cursor:
    """A class to manage terminal cursor operations."""

    @staticmethod
    def move(x: int, y: int) -> None:
        """Move the cursor to a specific position in the terminal.

        Args:
            x (int): The x-coordinate (column) to move the cursor to.
            y (int): The y-coordinate (row) to move the cursor to.
        """
        app.driver.write(f"\033[{y};{x}H")
        app.driver.flush()

    @staticmethod
    def move_no_flush(x: int, y: int) -> None:
        """Move the cursor to a specific position in the terminal without flushing to stdout.

        Args:
            x (int): The x-coordinate (column) to move the cursor to.
            y (int): The y-coordinate (row) to move the cursor to.
        """
        app.driver.write(f"\033[{y};{x}H")

    @staticmethod
    def show() -> None:
        """Show the terminal cursor."""
        app.driver.write("\033[?25h")
        app.driver.flush()

    @staticmethod
    def hide() -> None:
        """Hide the terminal cursor."""
        app.driver.write("\033[?25l")
        app.driver.flush()
