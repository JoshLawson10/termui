import sys


def clear_terminal() -> None:
    """Clear the terminal screen."""
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


def get_terminal_size() -> tuple[int, int]:
    """Get the current terminal size."""
    from os import get_terminal_size, terminal_size

    try:
        size: terminal_size = get_terminal_size()
        return (size.columns, size.lines)
    except OSError:
        return (80, 24)


def remove_ansi_escape_sequences(text: str) -> str:
    """Remove ANSI escape sequences from a string."""
    import re

    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def move_cursor_to(x: int, y: int) -> None:
    """Move the cursor to a specific position in the terminal."""
    sys.stdout.write(f"\033[{y};{x}H")
    sys.stdout.flush()


def hide_cursor() -> None:
    """Hide the terminal cursor."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    """Show the terminal cursor."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
