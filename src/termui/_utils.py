def clear_terminal() -> None:
    """Clear the terminal screen."""
    import os

    os.system("cls" if os.name == "nt" else "clear")
