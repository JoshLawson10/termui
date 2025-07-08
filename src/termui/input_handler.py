import sys
import tty
import termios
import select
from typing import Callable, Dict, List, Set, Optional
from .keybind import Keybind


class InputHandler:
    def __init__(self):
        self._keybinds: List[Keybind] = []
        self._current_keys: Set[str] = set()
        self._should_exit = False
        self._escape_sequences: Dict[str, str] = {
            "\x1b[A": "up",
            "\x1b[B": "down",
            "\x1b[C": "right",
            "\x1b[D": "left",
            "\x1b[1~": "home",
            "\x1b[4~": "end",
            "\x1b[3~": "delete",
            "\x1b[2~": "insert",
            "\x1b[5~": "pageup",
            "\x1b[6~": "pagedown",
            "\x1b[H": "home",
            "\x1b[F": "end",
            "\x1bOP": "f1",
            "\x1bOQ": "f2",
            "\x1bOR": "f3",
            "\x1bOS": "f4",
            "\x1b[15~": "f5",
            "\x1b[17~": "f6",
            "\x1b[18~": "f7",
            "\x1b[19~": "f8",
            "\x1b[20~": "f9",
            "\x1b[21~": "f10",
            "\x1b[23~": "f11",
            "\x1b[24~": "f12",
        }
        self._special_keys: Dict[str, str] = {
            "\x7f": "backspace",
            "\x1b": "escape",
            "\t": "tab",
            "\n": "enter",
            " ": "space",
        }

    def register_keybind(self, keybind: Keybind) -> None:
        """Register a new keybind with its associated action."""
        self._keybinds.append(keybind)

    def unregister_keybind(self, keybind: Keybind) -> None:
        """Unregister a keybind."""
        self._keybinds.remove(keybind)

    def _get_key(self) -> Optional[str]:
        """Get a single key press, handling escape sequences."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                char = sys.stdin.read(1)
                if char == "\x1b":
                    next_chars = sys.stdin.read(2)
                    seq = char + next_chars
                    if seq in self._escape_sequences:
                        return self._escape_sequences[seq]
                    else:
                        seq = char + sys.stdin.read(2)
                        if seq in self._escape_sequences:
                            return self._escape_sequences[seq]
                        return "escape"
                elif char in self._special_keys:
                    return self._special_keys[char]
                else:
                    return char.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    def process_input(self) -> None:
        """Process input and trigger appropriate actions."""
        key = self._get_key()
        if key is None:
            return

        # Handle modifier keys (ctrl, alt, shift)
        # For simplicity, we'll just track the key presses
        if key == "escape":
            self._current_keys.clear()
            return

        self._current_keys.add(key)

        for keybind in self._keybinds:
            if keybind.matches(self._current_keys):
                keybind.action()
                self._current_keys.clear()
                break

    def stop(self) -> None:
        """Stop the input handler."""
        self._should_exit = True
