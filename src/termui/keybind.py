from dataclasses import dataclass


@dataclass(frozen=True)
class Keybind:
    key: str
    action: str = ""
    description: str = ""
    visible: bool = True

    def parse_keybind(self) -> tuple[list[str], str]:
        """Parse the keybind into a list of keys and an action."""
        keys: list[str] = self.key.split("+")
        action: str = self.action if self.action else "default_action"
        return keys, action
