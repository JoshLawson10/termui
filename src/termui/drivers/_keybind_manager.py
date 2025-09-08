import inspect
from typing import Any

from termui import events
from termui.keybind import Keybind


class KeybindManager:
    """Manages keybinds and handles keybind matching."""

    def __init__(self) -> None:
        self.keybinds: list[Keybind] = []
        self._pressed_keys: set[str] = set()
        self._active_modifiers: set[str] = set()

    def register_keybind(self, keybind: Keybind) -> None:
        """Register a keybind.

        Args:
            keybind (Keybind): The keybind to register.
        """
        self.keybinds.append(keybind)

    def register_keybinds_from_object(self, obj: Any) -> None:
        """Register keybinds from an object's methods with @keybind decorator.

        Args:
            obj (Any): The object to register keybinds from.
        """
        for _, method in inspect.getmembers(obj, predicate=inspect.ismethod):
            info = getattr(method, "keybind_info", None)
            if info is not None:
                keybind = Keybind(
                    key=info["key"],
                    action=method,
                    description=info["description"],
                    visible=info["visible"],
                )
                self.register_keybind(keybind)

    def handle_key_event(self, event: events.Key) -> bool:
        """Handle a key event and check for keybind matches.

        Args:
            event (events.Key): The key event to handle.

        Returns:
            True if a keybind was triggered, False otherwise.
        """

        key = event.key

        # Handle modifier keys
        if key in {"ctrl", "shift", "alt", "meta"}:
            if key not in self._active_modifiers:
                self._active_modifiers.add(key)
            return False

        # Add the key to pressed keys
        self._pressed_keys.add(key)

        # Check for keybind matches
        for keybind in self.keybinds:
            if keybind.matches(self._pressed_keys | self._active_modifiers):
                keybind.action()
                self._pressed_keys.clear()
                return True

        return False

    def handle_key_release(self, key: str) -> None:
        """Handle key release events.

        Args:
            key (str): The key that was released.
        """
        if key in self._pressed_keys:
            self._pressed_keys.remove(key)

        if key in self._active_modifiers:
            self._active_modifiers.remove(key)

    def clear_pressed_keys(self) -> None:
        """Clear all pressed keys."""
        self._pressed_keys.clear()
        self._active_modifiers.clear()

    def get_visible_keybinds(self) -> list[Keybind]:
        """Get all visible keybinds.

        Returns:
            list[Keybind]: A list of all visible keybinds.
        """
        return [kb for kb in self.keybinds if kb.visible]
