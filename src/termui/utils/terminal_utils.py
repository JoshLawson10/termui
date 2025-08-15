import sys


def clear_terminal() -> None:
    """Clear the terminal screen."""
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


def get_terminal_size() -> tuple[int, int]:
    """Get the current terminal size.

    Returns:
        A tuple containing the width and height of the terminal.
    """
    from os import get_terminal_size, terminal_size

    try:
        size: terminal_size = get_terminal_size()
        return (size.columns, size.lines)
    except OSError:
        return (80, 24)


def set_terminal_size(width: int, height: int) -> None:
    """Set the size of the terminal.

    Args:
        width: The desired width of the terminal.
        height: The desired height of the terminal.
    """
    sys.stdout.write(f"\033[8;{height};{width}t")
    sys.stdout.flush()
