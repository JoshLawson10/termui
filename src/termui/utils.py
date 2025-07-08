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
