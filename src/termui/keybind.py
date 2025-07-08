from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Keybind:
    key: str
    action: Callable = lambda: None
    description: str = ""
    visible: bool = True

    def parse_keybind(self) -> tuple[list[str], Callable]:
        """Parse the keybind into a list of keys and an action."""
        keys: list[str] = self.key.split("+")
        return keys, self.action

    def matches(self, pressed_keys: set[str]) -> bool:
        """Check if the pressed keys match this keybind."""
        required_keys, _ = self.parse_keybind()
        return set(required_keys) == pressed_keys
