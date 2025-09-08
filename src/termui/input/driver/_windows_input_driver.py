import ctypes
import threading
from ctypes import Structure, Union, wintypes
from ctypes.wintypes import BOOL, CHAR, DWORD, SHORT, UINT, WCHAR, WORD
from typing import Optional

from termui._keys import Keys
from termui.input.driver._input_driver import InputDriver


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


WINDOWS_KEY_MAP: dict[int, Keys] = {
    8: Keys.Backspace,
    9: Keys.Tab,
    13: Keys.Enter,
    27: Keys.Escape,
    32: Keys.Space,
    33: Keys.PageUp,
    34: Keys.PageDown,
    35: Keys.End,
    36: Keys.Home,
    37: Keys.Left,
    38: Keys.Up,
    39: Keys.Right,
    40: Keys.Down,
    45: Keys.Insert,
    46: Keys.Delete,
    112: Keys.F1,
    113: Keys.F2,
    114: Keys.F3,
    115: Keys.F4,
    116: Keys.F5,
    117: Keys.F6,
    118: Keys.F7,
    119: Keys.F8,
    120: Keys.F9,
    121: Keys.F10,
    122: Keys.F11,
    123: Keys.F12,
}


class WindowsInputDriver(InputDriver):
    """Input manager for Windows systems."""

    def __init__(self):
        super().__init__()
        self.kernel32: ctypes.WinDLL = ctypes.windll.kernel32  # type: ignore
        self.stdin_handle: Optional[wintypes.HANDLE] = None
        self.original_console_mode: Optional[wintypes.DWORD] = None

    def setup(self):
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

    def teardown(self):
        """Restore terminal to original state on Windows."""
        if self.original_console_mode:
            self.kernel32.SetConsoleMode(self.stdin_handle, self.original_console_mode)

    def read_input(self):
        """Read input on Windows platform."""
        while self._running:
            # Read console input
            num_events = wintypes.DWORD()
            if not (
                self.kernel32.GetNumberOfConsoleInputEvents(
                    self.stdin_handle, ctypes.byref(num_events)
                )
                and num_events.value > 0
            ):
                continue

            input_event = InputEvent()
            events_read = wintypes.DWORD()

            if not (
                self.kernel32.ReadConsoleInputW(
                    self.stdin_handle,
                    ctypes.byref(input_event),
                    1,
                    ctypes.byref(events_read),
                )
                and events_read.value > 0
            ):
                continue

            if input_event.EventType == 1:  # KEY_EVENT
                key_event = input_event.Event.KeyEvent
                if not key_event.bKeyDown:
                    break

                char = key_event.uChar.UnicodeChar
                virtual_key_code = key_event.wVirtualKeyCode

                if virtual_key_code in WINDOWS_KEY_MAP:
                    key_name = WINDOWS_KEY_MAP[virtual_key_code].value
                    self._on_key_press(key_name, char if char.strip() else None)
                elif char:
                    self._on_key_press(char, char)

            elif input_event.EventType == 2:  # MOUSE_EVENT
                mouse_event = input_event.Event.MouseEvent
                x = mouse_event.dwMousePosition.X
                y = mouse_event.dwMousePosition.Y
                button_state = mouse_event.dwButtonState
                event_flags = mouse_event.dwEventFlags

                # Determine which button was pressed
                button = 0
                if button_state & 0x1:  # LEFTMOUSEBUTTON
                    button = 0
                elif button_state & 0x2:  # RIGHTMOUSEBUTTON
                    button = 2
                elif button_state & 0x4:  # MIDDLEMOUSEBUTTON
                    button = 1

                if event_flags == 0:  # Button click
                    if button_state:  # Button pressed
                        self._on_mouse_down(x, y, button)
                    else:  # Button released
                        self._on_mouse_up(x, y, button)

                elif event_flags == 1:  # Mouse moved
                    self._on_mouse_move(x, y, button)

                elif event_flags == 4:  # Mouse wheel
                    if button_state & 0xFF000000:  # Scroll down
                        self._on_mouse_scroll(x, y, "down")
                    else:  # Scroll up
                        self._on_mouse_scroll(x, y, "up")

            # Small sleep to prevent busy waiting
            threading.Event().wait(0.01)
