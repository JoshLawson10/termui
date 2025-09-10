import ctypes
import threading
from ctypes import Structure, Union, wintypes
from ctypes.wintypes import BOOL, CHAR, DWORD, SHORT, UINT, WCHAR, WORD
from typing import Optional

from termui.drivers._driver import Driver
from termui.logger import log


class COORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/coord-str"""

    _fields_ = [
        ("X", SHORT),
        ("Y", SHORT),
    ]


class uChar(Union):
    """https://docs.microsoft.com/en-us/windows/console/key-event-record-str"""

    _fields_ = [
        ("AsciiChar", CHAR),
        ("UnicodeChar", WCHAR),
    ]


class KEY_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/key-event-record-str"""

    _fields_ = [
        ("bKeyDown", BOOL),
        ("wRepeatCount", WORD),
        ("wVirtualKeyCode", WORD),
        ("wVirtualScanCode", WORD),
        ("uChar", uChar),
        ("dwControlKeyState", DWORD),
    ]


class MOUSE_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/mouse-event-record-str"""

    _fields_ = [
        ("dwMousePosition", COORD),
        ("dwButtonState", DWORD),
        ("dwControlKeyState", DWORD),
        ("dwEventFlags", DWORD),
    ]


class WINDOW_BUFFER_SIZE_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/window-buffer-size-record-str"""

    _fields_ = [("dwSize", COORD)]


class MENU_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/menu-event-record-str"""

    _fields_ = [("dwCommandId", UINT)]


class FOCUS_EVENT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/focus-event-record-str"""

    _fields_ = [("bSetFocus", BOOL)]


class InputEvent(Union):
    """https://docs.microsoft.com/en-us/windows/console/input-record-str"""

    _fields_ = [
        ("KeyEvent", KEY_EVENT_RECORD),
        ("MouseEvent", MOUSE_EVENT_RECORD),
        ("WindowBufferSizeEvent", WINDOW_BUFFER_SIZE_RECORD),
        ("MenuEvent", MENU_EVENT_RECORD),
        ("FocusEvent", FOCUS_EVENT_RECORD),
    ]


class INPUT_RECORD(Structure):
    """https://docs.microsoft.com/en-us/windows/console/input-record-str"""

    _fields_ = [("EventType", wintypes.WORD), ("Event", InputEvent)]


class WindowsDriver(Driver):
    """I/O manager for Windows systems."""

    def __init__(self):
        super().__init__()
        self.kernel32: ctypes.WinDLL = ctypes.windll.kernel32  # type: ignore
        self.stdin_handle: Optional[wintypes.HANDLE] = None
        self.original_console_mode: Optional[wintypes.DWORD] = None

    def setup(self) -> None:
        """Setup for Windows platform."""
        # Get standard input handle
        self.stdin_handle = self.kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE

        # Save original console mode
        self.original_console_mode = wintypes.DWORD()
        self.kernel32.GetConsoleMode(
            self.stdin_handle, ctypes.byref(self.original_console_mode)
        )

        # Set new console mode with ENABLE_MOUSE_INPUT and ENABLE_EXTENDED_FLAGS
        new_mode = self.original_console_mode.value | 0x0010 | 0x0080
        self.kernel32.SetConsoleMode(self.stdin_handle, new_mode)

        # Enable mouse tracking sequences
        self.write("\x1b[?1000h")  # Enable mouse tracking
        self.write("\x1b[?1006h")  # Enable SGR mouse mode
        self.flush()

    def teardown(self) -> None:
        """Restore terminal to original state on Windows."""
        if self.original_console_mode:
            self.kernel32.SetConsoleMode(self.stdin_handle, self.original_console_mode)

        # Disable mouse tracking
        self.write("\x1b[?1000l")
        self.write("\x1b[?1006l")
        self.flush()

    def read_input(self) -> None:
        """Read input on Windows platform."""
        while self._running:
            try:
                # Tick the parser to handle any timeouts
                self._tick_parser()

                # Read console input
                num_events = wintypes.DWORD()
                if not (
                    self.kernel32.GetNumberOfConsoleInputEvents(
                        self.stdin_handle, ctypes.byref(num_events)
                    )
                    and num_events.value > 0
                ):
                    threading.Event().wait(0.01)
                    continue

                input_records = (INPUT_RECORD * num_events.value)()
                events_read = wintypes.DWORD()

                if not (
                    self.kernel32.ReadConsoleInputW(
                        self.stdin_handle,
                        input_records,
                        num_events.value,
                        ctypes.byref(events_read),
                    )
                    and events_read.value > 0
                ):
                    continue

                for i in range(events_read.value):
                    input_record = input_records[i]

                    if input_record.EventType == 1:  # KEY_EVENT
                        key_event = input_record.Event.KeyEvent
                        if not key_event.bKeyDown:
                            continue

                        char = key_event.uChar.UnicodeChar
                        virtual_key_code = key_event.wVirtualKeyCode
                        control_key_state = key_event.dwControlKeyState

                        # Convert Windows key event to ANSI sequence or character
                        sequence = self._windows_key_to_sequence(
                            virtual_key_code, control_key_state, char
                        )

                        if sequence:
                            self._process_parser_events(sequence)

                    elif input_record.EventType == 2:  # MOUSE_EVENT
                        mouse_event = input_record.Event.MouseEvent
                        x = mouse_event.dwMousePosition.X
                        y = mouse_event.dwMousePosition.Y
                        button_state = mouse_event.dwButtonState
                        event_flags = mouse_event.dwEventFlags

                        # Convert Windows mouse event to SGR mouse sequence
                        sequence = self._windows_mouse_to_sequence(
                            x, y, button_state, event_flags
                        )

                        if sequence:
                            self._process_parser_events(sequence)

            except Exception as e:
                log.error(f"Windows input error: {e}")
                threading.Event().wait(0.01)

    @staticmethod
    def _windows_key_to_sequence(vk_code: int, control_state: int, char: str) -> str:
        """Convert Windows virtual key code to ANSI sequence or character.

        Args:
            vk_code: The virtual key code.
            control_state: The control key state.
            char: The character representation of the key.

        Returns:
            str: The key sequence
        """
        # Check for modifier keys
        ctrl_pressed = control_state & 0x0008  # RIGHT_CTRL_PRESSED | LEFT_CTRL_PRESSED
        alt_pressed = control_state & 0x0003  # RIGHT_ALT_PRESSED | LEFT_ALT_PRESSED
        shift_pressed = control_state & 0x0010  # SHIFT_PRESSED

        # Special key mappings
        special_keys = {
            8: "\x7f",  # Backspace
            9: "\t",  # Tab
            13: "\r",  # Enter
            27: "\x1b",  # Escape
            32: " ",  # Space
            33: "\x1b[5~",  # Page Up
            34: "\x1b[6~",  # Page Down
            35: "\x1b[F",  # End
            36: "\x1b[H",  # Home
            37: "\x1b[D",  # Left Arrow
            38: "\x1b[A",  # Up Arrow
            39: "\x1b[C",  # Right Arrow
            40: "\x1b[B",  # Down Arrow
            45: "\x1b[2~",  # Insert
            46: "\x1b[3~",  # Delete
            112: "\x1bOP",  # F1
            113: "\x1bOQ",  # F2
            114: "\x1bOR",  # F3
            115: "\x1bOS",  # F4
            116: "\x1b[15~",  # F5
            117: "\x1b[17~",  # F6
            118: "\x1b[18~",  # F7
            119: "\x1b[19~",  # F8
            120: "\x1b[20~",  # F9
            121: "\x1b[21~",  # F10
            122: "\x1b[23~",  # F11
            123: "\x1b[24~",  # F12
        }

        if vk_code in special_keys:
            base_seq = special_keys[vk_code]

            # Apply modifiers for special keys
            if ctrl_pressed or alt_pressed or shift_pressed:
                modifier = 1
                if shift_pressed:
                    modifier += 1
                if alt_pressed:
                    modifier += 2
                if ctrl_pressed:
                    modifier += 4

                # Modify arrow keys and function keys with modifiers
                if vk_code in (37, 38, 39, 40):  # Arrow keys
                    return f"\x1b[1;{modifier}{base_seq[-1]}"
                if 112 <= vk_code <= 123:  # Function keys
                    if base_seq.startswith("\x1bO"):
                        return f"\x1b[1;{modifier}{base_seq[-1]}"
                    return base_seq.replace("~", f";{modifier}~")

            return base_seq

        # Handle control characters
        if ctrl_pressed and char and ord(char) < 32:
            return char

        # Regular character
        if char and char.isprintable():
            return char

        return ""

    @staticmethod
    def _windows_mouse_to_sequence(x: int, y: int, button_state: int, event_flags: int) -> str:
        """Convert Windows mouse event to SGR mouse sequence.

        Args:
            x: The x-coordinate of the mouse event.
            y: The y-coordinate of the mouse event.
            button_state: The state of the mouse buttons.
            event_flags: The flags for the mouse event.

        Returns:
            str: The SGR mouse sequence.
        """
        # Determine button
        button = 0
        if button_state & 0x1:  # Left button
            button = 0
        elif button_state & 0x2:  # Right button
            button = 2
        elif button_state & 0x4:  # Middle button
            button = 1

        # Handle different event types
        match event_flags:
            case 0:
                if button_state & 0xFF:  # Any button pressed
                    return f"\x1b[<{button};{x + 1};{y + 1}M"
                return f"\x1b[<{button};{x + 1};{y + 1}m"  # Button released
            case 1:  # Mouse moved
                return f"\x1b[<{button + 32};{x + 1};{y + 1}M"  # Movement flag
            case 4:  # Mouse wheel
                wheel_button = 64 + (0 if button_state > 0 else 1)  # Scroll up/down
                return f"\x1b[<{wheel_button};{x + 1};{y + 1}M"
        return ""
