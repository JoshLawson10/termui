import sys


def clear_terminal() -> None:
    """Clear the terminal screen."""
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


def set_terminal_size(width: int, height: int) -> None:
    """Set the size of the terminal.

    Args:
        width: The desired width of the terminal.
        height: The desired height of the terminal.
    """
    sys.stdout.write(f"\033[8;{height};{width}t")
    sys.stdout.flush()
