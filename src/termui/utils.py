def clear_terminal() -> None:
    """Clear the terminal screen."""
    print("\033[H\033[J", end="", flush=True)


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
    print(f"\033[{y};{x}H", end="", flush=True)
