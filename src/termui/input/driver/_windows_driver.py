from __future__ import annotations

import asyncio
import ctypes
import msvcrt
import sys
import threading
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from ctypes import byref, Structure, Union, wintypes
from ctypes.wintypes import BOOL, CHAR, DWORD, HANDLE, SHORT, UINT, WCHAR, WORD
from threading import Event, Thread
from typing import Callable, IO, List, Optional, TYPE_CHECKING

from termui._driver import Driver

from termui._xterm_parser import XTermParser
from termui.events import Resize
from termui.input._writer_thread import WriterThread
from termui.message import Message
from termui.utils.geometry import Size

if TYPE_CHECKING:
    from termui.app import App

KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore

# Console input modes
ENABLE_ECHO_INPUT = 0x0004
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_INSERT_MODE = 0x0020
ENABLE_LINE_INPUT = 0x0002
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_WINDOW_INPUT = 0x0008
ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

# Console output modes
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
DISABLE_NEWLINE_AUTO_RETURN = 0x0008
ENABLE_LVB_GRID_WORLDWIDE = 0x0010

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11

WAIT_TIMEOUT = 0x00000102

GetStdHandle = KERNEL32.GetStdHandle
GetStdHandle.argtypes = [wintypes.DWORD]
GetStdHandle.restype = wintypes.HANDLE


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


def set_console_mode(file: IO, mode: int) -> bool:
    """Set the console mode for a given file (stdout or stdin).

    Args:
        file: A file like object.
        mode: New mode.

    Returns:
        True on success, otherwise False.
    """
    windows_filehandle = msvcrt.get_osfhandle(file.fileno())  # type: ignore
    success = KERNEL32.SetConsoleMode(windows_filehandle, mode)
    return success


def get_console_mode(file: IO) -> int:
    """Get the console mode for a given file (stdout or stdin)

    Args:
        file: A file-like object.

    Returns:
        The current console mode.
    """
    windows_filehandle = msvcrt.get_osfhandle(file.fileno())  # type: ignore
    mode = wintypes.DWORD()
    KERNEL32.GetConsoleMode(windows_filehandle, ctypes.byref(mode))
    return mode.value


def enable_application_mode() -> Callable[[], None]:
    """Enable application mode.

    Returns:
        A callable that will restore terminal to previous state.
    """

    terminal_in = sys.stdin
    terminal_out = sys.stdout

    current_console_mode_in = get_console_mode(terminal_in)
    current_console_mode_out = get_console_mode(terminal_out)

    def restore() -> None:
        """Restore console mode to previous settings"""
        set_console_mode(terminal_in, current_console_mode_in)
        set_console_mode(terminal_out, current_console_mode_out)

    set_console_mode(
        terminal_out, current_console_mode_out | ENABLE_VIRTUAL_TERMINAL_PROCESSING
    )
    set_console_mode(terminal_in, ENABLE_VIRTUAL_TERMINAL_INPUT)
    return restore


def wait_for_handles(handles: List[HANDLE], timeout: int = -1) -> Optional[HANDLE]:
    """
    Waits for multiple handles. (Similar to 'select') Returns the handle which is ready.
    Returns `None` on timeout.
    http://msdn.microsoft.com/en-us/library/windows/desktop/ms687025(v=vs.85).aspx
    """
    arrtype = HANDLE * len(handles)
    handle_array = arrtype(*handles)

    ret: int = KERNEL32.WaitForMultipleObjects(
        len(handle_array), handle_array, BOOL(False), DWORD(timeout)
    )

    if ret == WAIT_TIMEOUT:
        return None

    return handles[ret]


class EventMonitor(threading.Thread):
    """A thread to send key / window events to the loop."""

    def __init__(
        self,
        loop: AbstractEventLoop,
        app: App,
        exit_event: threading.Event,
        process_event: Callable[[Message], None],
    ) -> None:
        self.loop = loop
        self.app = app
        self.exit_event = exit_event
        self.process_event = process_event
        super().__init__(name="input")

    def run(self) -> None:
        parser = XTermParser(debug=True)

        try:
            MAX_EVENTS = 1024
            KEY_EVENT = 0x0001
            WINDOW_BUFFER_SIZE_EVENT = 0x0004

            arrtype = INPUT_RECORD * MAX_EVENTS
            input_records = arrtype()
            ReadConsoleInputW = KERNEL32.ReadConsoleInputW
            keys: List[str] = []
            append_key = keys.append

            while not self.exit_event.is_set():
                for event in parser.tick():
                    if isinstance(event, Event):
                        self.process_event(event)

                if wait_for_handles([GetStdHandle(STD_INPUT_HANDLE)], 100) is None:
                    continue

                # Get new events
                ReadConsoleInputW(
                    GetStdHandle(STD_INPUT_HANDLE),
                    byref(input_records),
                    MAX_EVENTS,
                    byref(wintypes.DWORD(0)),
                )
                read_input_records = input_records[: wintypes.DWORD(0).value]

                del keys[:]
                new_size: Optional[tuple[int, int]] = None

                for input_record in read_input_records:
                    event_type = input_record.EventType

                    if event_type == KEY_EVENT:
                        # Key event, store unicode char in keys list
                        key_event = input_record.Event.KeyEvent
                        key = key_event.uChar.UnicodeChar
                        if key_event.bKeyDown:
                            if (
                                key_event.dwControlKeyState
                                and key_event.wVirtualKeyCode == 0
                            ):
                                continue
                            append_key(key)
                    elif event_type == WINDOW_BUFFER_SIZE_EVENT:
                        # Window size changed, store size
                        size = input_record.Event.WindowBufferSizeEvent.dwSize
                        new_size = (size.X, size.Y)

                if keys:
                    # Process keys
                    for event in parser.feed(
                        "".join(keys).encode("utf-16", "surrogatepass").decode("utf-16")
                    ):
                        if isinstance(event, Event):
                            self.process_event(event)
                if new_size is not None:
                    self.on_size_change(*new_size)

        except Exception as error:
            self.app.log.error(f"EVENT MONITOR ERROR: {error}")

    def on_size_change(self, width: int, height: int) -> None:
        """Called when terminal size changes."""
        size = Size(width, height)
        event = Resize(size)
        coro = self.app.post_message(event)
        if coro is not None:
            run_coroutine_threadsafe(coro, loop=self.loop)


class WindowsDriver(Driver):
    """Windows-specific input driver implementation."""

    def __init__(
        self,
        app: "App",
        *,
        debug: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
    ) -> None:
        """Initialize Windows driver.

        Args:
            app: The App instance.
            debug: Enable debug mode.
            mouse: Enable mouse support.
            size: Initial size of the terminal or `None` to detect.
        """
        super().__init__(app, debug=debug, mouse=mouse, size=size)
        self._app = app
        self._file = sys.stdout
        self.exit_event = Event()
        self._event_thread: Thread | None = None
        self._restore_console: Callable[[], None] | None = None
        self._writer_thread: WriterThread | None = None

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """
        assert self._writer_thread is not None, "Driver must be in application mode"
        self._writer_thread.write(data)

    def _enable_mouse_support(self) -> None:
        """Enable reporting of mouse events."""
        if not self._mouse:
            return
        write = self.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE
        self.flush()

    def _disable_mouse_support(self) -> None:
        """Disable reporting of mouse events."""
        if not self._mouse:
            return
        write = self.write
        write("\x1b[?1000l")
        write("\x1b[?1003l")
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.flush()

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.write("\x1b[?2004l")

    def start_application_mode(self) -> None:
        """Start application mode."""
        loop = asyncio.get_running_loop()

        self._restore_console = enable_application_mode()

        self._writer_thread = WriterThread(self._file)
        self._writer_thread.start()

        self.write("\x1b[?1049h")  # Enable alt screen
        self._enable_mouse_support()
        self.write("\x1b[?25l")  # Hide cursor
        self.write("\033[?1003h")
        self.write("\033[?1004h")  # Enable FocusIn/FocusOut.
        self.flush()
        self._enable_bracketed_paste()

        self._event_thread = EventMonitor(
            loop, self._app, self.exit_event, self.process_message
        )
        self._event_thread.start()

    def disable_input(self) -> None:
        """Disable further input."""
        try:
            if not self.exit_event.is_set():
                self._disable_mouse_support()
                self.exit_event.set()
                if self._event_thread is not None:
                    self._event_thread.join()
                    self._event_thread = None
                self.exit_event.clear()
        except Exception as e:
            self._app.log.error(f"Error disabling input: {e}")

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self._disable_bracketed_paste()
        self.disable_input()

        # Disable alt screen, show cursor
        self.write("\x1b[?1049l" + "\x1b[?25h")
        self.write("\033[?1004l")  # Disable FocusIn/FocusOut.
        self.flush()

    def close(self) -> None:
        """Perform cleanup."""
        if self._writer_thread is not None:
            self._writer_thread.stop()
        if self._restore_console:
            self._restore_console()
