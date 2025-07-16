from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Keybind:
    """A class representing a keybind.

    Attributes
    ----------
    key : str
        The key or combination of keys that trigger the action.
    action : Callable
        The action to be executed when the keybind is triggered.
    description : str
        A description of the keybind, used for documentation or UI display.
    visible : bool
        Whether the keybind should be visible in the UI.
    """

    key: str
    action: Callable = lambda: None
    description: str = ""
    visible: bool = True

    def parse_keybind(self) -> tuple[list[str], Callable]:
        """Parse the keybind into a list of keys and an action."""
        keys: list[str] = self.key.split("+")
        return keys, self.action

    def keys(self) -> frozenset[str]:
        """Get the keys associated with this keybind."""
        return frozenset(self.key.split("+"))

    def matches(self, pressed_keys: set[str]) -> bool:
        """Check if the pressed keys match this keybind."""
        return self.keys() == pressed_keys


def keybind(
    key: str,
    description: str = "",
    visible: bool = True,
):
    """Decorator to create a keybind for a method.

    Parameters
    ----------
    key : str
        The key or combination of keys that trigger the action.
    description : str, optional
        A description of the keybind, by default "".
    visible : bool, optional
        Whether the keybind should be visible in the UI, by default True.
    """

    def decorator(func: Callable) -> Callable:
        func._keybind_info = {
            "key": key,
            "description": description,
            "visible": visible,
        }
        return func

    return decorator
