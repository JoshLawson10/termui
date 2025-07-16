import os
import sys
import tty
import termios
import select
import threading
from typing import Dict, List, Set, Optional
from contextlib import contextmanager
from .keybind import Keybind


class InputHandler:
    def __init__(self):
        self._keybinds: List[Keybind] = []
        self._current_keys: Set[str] = set()
        self._should_exit = False
        self._original_term_settings = None
        self._lock = threading.Lock()

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
            "\r": "enter",
            " ": "space",
            "\x03": "ctrl+c",
            "\x1a": "ctrl+z",
        }

        self._setup_terminal()

    def _setup_terminal(self) -> None:
        """Setup terminal in raw mode with proper error handling."""
        if not sys.stdin.isatty():
            return

        try:
            fd = sys.stdin.fileno()
            self._original_term_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        except (termios.error, OSError) as e:
            print(f"Warning: Could not setup terminal: {e}", file=sys.stderr)

    def _restore_terminal(self) -> None:
        """Restore terminal to original state."""
        if self._original_term_settings is None:
            return

        try:
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, self._original_term_settings)
        except (termios.error, OSError) as e:
            print(f"Warning: Could not restore terminal: {e}", file=sys.stderr)

    @contextmanager
    def _terminal_context(self):
        """Context manager for terminal state."""
        self._setup_terminal()
        try:
            yield
        finally:
            self._restore_terminal()

    def register_keybind(self, keybind: Keybind) -> None:
        """Register a new keybind with its associated action."""
        with self._lock:
            self._keybinds.append(keybind)

    def unregister_keybind(self, keybind: Keybind) -> None:
        """Unregister a keybind."""
        with self._lock:
            if keybind in self._keybinds:
                self._keybinds.remove(keybind)

    def clear_keybinds(self) -> None:
        """Clear all registered keybinds."""
        with self._lock:
            self._keybinds.clear()

    def get_keybinds(self) -> List[Keybind]:
        """Get a list of all registered keybinds."""
        with self._lock:
            return self._keybinds.copy()

    def _get_key(self) -> Optional[str]:
        """Get a single key press, handling escape sequences."""
        if not sys.stdin.isatty():
            return None

        try:
            rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
            if not rlist:
                return None

            char = sys.stdin.read(1)
            if not char:
                return None

            if char == "\x1b":
                rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
                if rlist:
                    next_chars = sys.stdin.read(2)
                    seq = char + next_chars

                    if seq in self._escape_sequences:
                        return self._escape_sequences[seq]

                    rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if rlist:
                        extra_char = sys.stdin.read(1)
                        longer_seq = seq + extra_char
                        if longer_seq in self._escape_sequences:
                            return self._escape_sequences[longer_seq]

                return "escape"

            if char in self._special_keys:
                return self._special_keys[char]

            if ord(char) < 32:
                return f"ctrl+{chr(ord(char) + 64).lower()}"

            return char.lower()

        except (OSError, IOError):
            return None

    def process_input(self) -> None:
        """Process input and trigger appropriate actions."""
        if self._should_exit:
            return

        key = self._get_key()
        if key is None:
            return

        if key == "ctrl+c":
            self._should_exit = True
            return

        if key == "escape":
            self._current_keys.clear()
            return

        self._current_keys.add(key)

        with self._lock:
            for keybind in self._keybinds:
                if keybind.matches(self._current_keys):
                    try:
                        keybind.action()
                    except Exception as e:
                        print(f"Error in keybind action: {e}", file=sys.stderr)
                    self._current_keys.clear()
                    break

    def should_exit(self) -> bool:
        """Check if the input handler should exit."""
        return self._should_exit

    def stop(self) -> None:
        """Stop the input handler gracefully."""
        self._should_exit = True
        self._restore_terminal()

    def __enter__(self):
        """Context manager entry."""
        self._setup_terminal()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._restore_terminal()
