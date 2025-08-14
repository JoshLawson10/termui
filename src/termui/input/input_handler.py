import re
import select
import sys
import termios
import tty
from typing import Optional

from termui.events import InputEvent, KeyEvent, MouseEvent
from .keybind import Keybind


class InputHandler:
    def __init__(self):
        self._keybinds: list[Keybind] = []
        self._current_keys: set[str] = set()
        self._should_exit = False
        self._mouse_enabled = False
        self._current_mouse_x: int = 0
        self._current_mouse_y: int = 0
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

        self._set_raw_mode(True)

    def register_keybind(self, keybind: Keybind) -> None:
        """Register a new keybind with its associated action."""
        self._keybinds.append(keybind)

    def unregister_keybind(self, keybind: Keybind) -> None:
        """Unregister a keybind."""
        self._keybinds.remove(keybind)

    def clear_keybinds(self) -> None:
        """Clear all registered keybinds."""
        self._keybinds.clear()

    def get_keybinds(self) -> list[Keybind]:
        """Get a list of all registered keybinds."""
        return self._keybinds

    def enable_mouse(self) -> None:
        """Enable mouse tracking in the terminal."""
        if not self._mouse_enabled:
            sys.stdout.write("\033[?1003h\033[?1006h")
            sys.stdout.flush()
            self._mouse_enabled = True

    def disable_mouse(self) -> None:
        """Disable mouse tracking in the terminal."""
        if self._mouse_enabled:
            sys.stdout.write("\033[?1003l\033[?1006l")
            sys.stdout.flush()
            self._mouse_enabled = False

    def get_mouse_position(self) -> Optional[tuple[int, int]]:
        """Get the current mouse position by requesting it from the terminal.

        Note: This is a blocking call that waits for the user to move or click the mouse.
        For non-blocking mouse handling, use enable_mouse() and register callbacks instead.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        mouse_was_enabled = self._mouse_enabled

        try:
            tty.setraw(fd)
            if not self._mouse_enabled:
                sys.stdout.write("\033[?1003h\033[?1006h")
                sys.stdout.flush()

            buf = ""
            while True:
                ch = sys.stdin.read(1)
                buf += ch
                if ch == "M" or ch == "m":
                    break

            match = re.search(r"\x1b\[<\d+;(\d+);(\d+)[mM]", buf)
            if match:
                col = int(match.group(1))
                row = int(match.group(2))
                return (col, row)
            else:
                return None

        finally:
            # Restore old terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # Restore mouse tracking state
            if not mouse_was_enabled:
                sys.stdout.write("\033[?1003l\033[?1006l")
                sys.stdout.flush()

    def _parse_mouse_event(self, sequence: str) -> Optional[MouseEvent]:
        """Parse a mouse escape sequence into a MouseEvent."""
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

    async def _get_input_event_async(self) -> Optional[InputEvent]:
        """Get a single key press, handling escape sequences and mouse events."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                char = sys.stdin.read(1)
                if char == "\x1b":
                    next_char = sys.stdin.read(1)
                    if next_char == "[":
                        third_char = sys.stdin.read(1)
                        if third_char == "<":
                            mouse_buf = "\x1b[<"
                            while True:
                                ch = sys.stdin.read(1)
                                mouse_buf += ch
                                if ch == "M" or ch == "m":
                                    break

                            if self._mouse_enabled:
                                return self._parse_mouse_event(mouse_buf)
                        else:
                            seq = char + next_char + third_char
                            if seq in self._escape_sequences:
                                return KeyEvent(self._escape_sequences[seq])
                            else:
                                fourth_char = sys.stdin.read(1)
                                longer_seq = seq + fourth_char
                                if longer_seq in self._escape_sequences:
                                    return KeyEvent(self._escape_sequences[longer_seq])
                                return KeyEvent("escape")
                    else:
                        # Two character escape sequence
                        seq = char + next_char
                        if seq in self._escape_sequences:
                            return KeyEvent(self._escape_sequences[seq])
                        return KeyEvent("escape")
                elif char in self._special_keys:
                    return KeyEvent(self._special_keys[char])
                else:
                    return KeyEvent(char.lower())
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    async def process_input(self) -> Optional[InputEvent]:
        """Process input and trigger appropriate actions."""
        event = await self._get_input_event_async()
        if event is None:
            return None

        if isinstance(event, KeyEvent):
            if event.key == "escape":
                self._current_keys.clear()
                return event

            self._current_keys.add(event.key)

        elif isinstance(event, MouseEvent):
            self._current_mouse_x = event.x
            self._current_mouse_y = event.y
            # Handle mouse events here if needed

        for keybind in self._keybinds:
            if keybind.matches(self._current_keys):
                keybind.action()
                self._current_keys.clear()
                break

        return event

    def _set_raw_mode(self, enable: bool):
        fd = sys.stdin.fileno()
        if enable:
            self._original_term_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
        elif self._original_term_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, self._original_term_settings)

    def stop(self) -> None:
        """Stop the input handler and clean up."""
        self.disable_mouse()
        self._set_raw_mode(False)
        self._should_exit = True
