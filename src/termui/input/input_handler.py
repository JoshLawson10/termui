import re
import select
import sys
from dataclasses import dataclass
from typing import Optional

from termui.events import InputEvent, KeyEvent, MouseEvent
from .keybind import Keybind


@dataclass
class MouseState:
    """Represents the state of the mouse.

    Args:
        enabled: Whether mouse tracking is enabled.
        x: The current x-coordinate of the mouse.
        y: The current y-coordinate of the mouse.
    """

    enabled: bool = False
    x: int = 0
    y: int = 0


class InputHandler:
    """Handles terminal input including keyboard and mouse events.

    The InputHandler manages raw terminal input, processes escape sequences,
    handles keybindings, and provides mouse tracking functionality.
    """

    def __init__(self) -> None:
        """Initialize the input handler with default settings and mappings."""
        self._keybinds: list[Keybind] = []
        """A list of all registered keybinds."""
        self._current_keys: set[str] = set()
        """A set of currently pressed keys. Used for multi-key keybinds."""
        self._should_exit = False
        """Flag indicating whether the application should exit."""
        self._mouse = MouseState()
        """The current state of the mouse."""

        self._escape_sequences: dict[str, str] = {
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
        self._special_keys: dict[str, str] = {
            "\x7f": "backspace",
            "\x1b": "escape",
            "\t": "tab",
            "\n": "enter",
            " ": "space",
        }

    def register_keybind(self, keybind: Keybind) -> None:
        """Register a new keybind with its associated action.

        Args:
            keybind: The keybind to register.
        """
        self._keybinds.append(keybind)

    def unregister_keybind(self, keybind: Keybind) -> None:
        """Unregister a keybind.

        Args:
            keybind: The keybind to remove from the registered keybinds.
        """
        self._keybinds.remove(keybind)

    def clear_keybinds(self) -> None:
        """Clear all registered keybinds."""
        self._keybinds.clear()

    def get_keybinds(self) -> list[Keybind]:
        """Get a list of all registered keybinds.

        Returns:
            A list of all currently registered keybinds.
        """
        return self._keybinds

    def enable_mouse(self) -> None:
        """Enable mouse tracking in the terminal.

        Enables SGR mouse reporting mode for precise mouse event handling.
        """
        if not self._mouse.enabled:
            sys.stdout.write("\033[?1003h\033[?1006h")
            sys.stdout.flush()
            self._mouse.enabled = True

    def disable_mouse(self) -> None:
        """Disable mouse tracking in the terminal.

        Disables SGR mouse reporting mode.
        """
        if self._mouse.enabled:
            sys.stdout.write("\033[?1003l\033[?1006l")
            sys.stdout.flush()
            self._mouse.enabled = False

    def get_mouse_position(self) -> Optional[tuple[int, int]]:
        """Get the current mouse position by requesting it from the terminal.

        This is a blocking call that waits for the user to move or click the mouse.
        For non-blocking mouse handling, use enable_mouse() and register callbacks instead.

        Returns:
            A tuple (column, row) of the mouse position, or None if unable
            to retrieve the position.
        """
        if not self._mouse.enabled:
            sys.stdout.write("\033[?1003h\033[?1006h")
            sys.stdout.flush()

        buf = ""
        while True:
            ch = sys.stdin.read(1)
            buf += ch
            if ch in ("M", "m"):
                break

        match = re.search(r"\x1b\[<\d+;(\d+);(\d+)[mM]", buf)
        if match:
            col = int(match.group(1))
            row = int(match.group(2))
            return (col, row)

        return None

    def _parse_mouse_event(self, sequence: str) -> Optional[MouseEvent]:
        """Parse a mouse escape sequence into a MouseEvent.

        Args:
            sequence: The escape sequence to parse.

        Returns:
            A MouseEvent object if parsing successful, None otherwise.
        """
        # SGR mode: \x1b[<button;col;rowM (press) or \x1b[<button;col;rowm (release)
        match = re.search(r"\x1b\[<(\d+);(\d+);(\d+)([mM])", sequence)
        if not match:
            return None

        button_code = int(match.group(1))
        col = int(match.group(2))
        row = int(match.group(3))
        is_press = match.group(4) == "M"

        # Decode button from button code
        button = button_code & 3  # Bottom 2 bits indicate button
        is_drag = bool(button_code & 32)  # Bit 5 indicates drag
        is_move = bool(button_code & 64)  # Bit 6 indicates mouse move

        if is_move and not is_press:
            event_type = "move"
        elif is_drag:
            event_type = "drag"
        elif is_press:
            event_type = "press"
        else:
            event_type = "release"

        return MouseEvent(col, row, button, event_type)

    def _read_char(self) -> str:
        """Read a single character from stdin (blocking)."""
        return sys.stdin.read(1)

    def _parse_mouse_event_sequence(self) -> Optional[MouseEvent]:
        """Read and parse a mouse escape sequence into a MouseEvent."""
        mouse_buf = "\x1b[<"
        while True:
            ch = self._read_char()
            mouse_buf += ch
            if ch in {"M", "m"}:
                break
        return self._parse_mouse_event(mouse_buf) if self._mouse.enabled else None

    def _parse_escape_sequence(self) -> Optional[InputEvent]:
        """Parse an escape sequence into a KeyEvent or MouseEvent."""
        next_char = self._read_char()
        if next_char != "[":
            # Two-char escape (like ESC + something)
            seq = "\x1b" + next_char
            return KeyEvent(self._escape_sequences.get(seq, "escape"))

        third_char = self._read_char()
        if third_char == "<":
            return self._parse_mouse_event_sequence()

        seq = "\x1b[" + third_char
        if seq in self._escape_sequences:
            return KeyEvent(self._escape_sequences[seq])

        # try longer sequence
        fourth_char = self._read_char()
        longer_seq = seq + fourth_char
        if longer_seq in self._escape_sequences:
            return KeyEvent(self._escape_sequences[longer_seq])

        return KeyEvent("escape")

    async def _get_input_event_async(self) -> Optional[InputEvent]:
        """Get a single input event, handling escape sequences and mouse events."""
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if not rlist:
            return None

        char = self._read_char()
        event: Optional[InputEvent] = None

        if char == "\x1b":
            event = self._parse_escape_sequence()
        elif char in self._special_keys:
            event = KeyEvent(self._special_keys[char])
        else:
            event = KeyEvent(char.lower())

        return event

    async def process_input(self) -> Optional[InputEvent]:
        """Process input and trigger appropriate keybind actions.

        Returns:
            The input event that was processed, or None if no input was available.
        """
        event = await self._get_input_event_async()
        if event is None:
            return None

        if isinstance(event, KeyEvent):
            if event.key == "escape":
                self._current_keys.clear()
                return event

            self._current_keys.add(event.key)

        elif isinstance(event, MouseEvent):
            self._mouse.x = event.x
            self._mouse.y = event.y
            # Handle mouse events here if needed

        for keybind in self._keybinds:
            if keybind.matches(self._current_keys):
                keybind.action()
                self._current_keys.clear()
                break

        return event

    def stop(self) -> None:
        """Stop the input handler and clean up terminal settings.

        Disables mouse tracking, restores normal terminal mode, and sets
        the exit flag.
        """
        self.disable_mouse()
        self._should_exit = True
