from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Keybind:
    """A keybind that maps key combinations to actions.

    Args:
        key: The key or combination of keys that trigger the action.
             Multiple keys should be separated by '+' (e.g., "ctrl+c").
        action: The callable to execute when the keybind is triggered.
        description: A human-readable description of what the keybind does.
        visible: Whether the keybind should be shown in help displays or UI.
    """

    key: str
    """The key or combination of keys that trigger the action."""
    action: Callable = lambda: None
    """The callable to execute when the keybind is triggered."""
    description: str = ""
    """A human-readable description of what the keybind does."""
    visible: bool = True
    """Whether the keybind should be shown in help displays or UI."""

    def parse_keybind(self) -> tuple[list[str], Callable]:
        """Parse the keybind into a list of keys and an action.

        Returns:
            A tuple containing (list of individual keys, action callable).
            For example, "ctrl+c" becomes (["ctrl", "c"], action).
        """
        keys: list[str] = self.key.split("+")
        return keys, self.action

    def matches(self, pressed_keys: set[str]) -> bool:
        """Check if the currently pressed keys match this keybind.

        Args:
            pressed_keys: Set of currently pressed key identifiers.

        Returns:
            True if the pressed keys exactly match the required keys
            for this keybind, False otherwise.
        """
        required_keys, _ = self.parse_keybind()
        return set(required_keys) == pressed_keys


def keybind(
    key: str,
    description: str = "",
    visible: bool = True,
):
    """Decorator to create a keybind for a method.

    This decorator marks a method as a keybind handler. The decorated method
    will be automatically registered as a keybind when the containing class
    is initialized.

    Args:
        key: The key or combination of keys that trigger the action.
        description: A human-readable description of the keybind's function.
        visible: Whether the keybind should be visible in help displays.

    Returns:
        The decorator function that adds keybind metadata to the method.

    Example:
        ```python
        @keybind("ctrl+s", "Save the current document")
        def save_document(self):
            # Save logic here
            pass
        ```
    """

    def decorator(func: Callable) -> Callable:
        func.keybind_info = {
            "key": key,
            "description": description,
            "visible": visible,
        }
        return func

    return decorator
