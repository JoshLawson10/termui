import fcntl
import os
import select
import sys
import termios
import tty

from termui._keys import Keys
from termui.drivers._driver import Driver


class UnixDriver(Driver):
    """I/O manager for Unix-like systems (Linux, macOS)."""

    def __init__(self):
        super().__init__()
        self._original_terminal_settings = None
        self._original_flags = None

    def setup(self):
        """Setup for Unix-like platforms."""
        # Save original terminal settings
        self._original_terminal_settings = termios.tcgetattr(sys.stdin)

        # Set terminal to raw mode
        tty.setraw(sys.stdin.fileno())

        # Enable mouse tracking
        self.write("\x1b[?1000h")  # Enable mouse tracking
        self.write("\x1b[?1003h")  # Enable any-event mouse tracking
        self.write("\x1b[?1015h")  # Enable urxvt mouse mode
        self.flush()

        # Set stdin to non-blocking
        fd = sys.stdin.fileno()
        self._original_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, self._original_flags | os.O_NONBLOCK)

    def teardown(self):
        """Restore terminal to original state on Unix."""
        # Restore terminal settings
        if self._original_terminal_settings:
            termios.tcsetattr(
                sys.stdin, termios.TCSADRAIN, self._original_terminal_settings
            )

        # Restore file flags
        if self._original_flags is not None:
            fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, self._original_flags)

        # Disable mouse tracking
        self.write("\x1b[?1000l")  # Disable mouse tracking
        self.write("\x1b[?1003l")  # Disable any-event mouse tracking
        self.write("\x1b[?1015l")  # Disable urxvt mouse mode
        self.flush()

    def read_input(self):
        """Read input on Unix-like platforms."""
        buffer = ""
        try:
            while self._running:
                # Use select to check if there's input available
                r, _, _ = select.select([sys.stdin], [], [], 0.1)
                if not r:
                    continue

                # Read available input
                try:
                    char = sys.stdin.read(1)
                    if not char:
                        continue

                    # Handle escape sequences
                    if char == "\x1b":
                        buffer = char
                        # Read more characters with a short timeout
                        while True:
                            r, _, _ = select.select([sys.stdin], [], [], 0.01)
                            if not r:
                                break
                            next_char = sys.stdin.read(1)
                            if not next_char:
                                break
                            buffer += next_char

                        # Parse the ANSI sequence
                        self._parse_ansi_sequence(buffer)
                        buffer = ""
                    else:
                        # Regular character
                        if ord(char) == 127:  # Backspace
                            self._on_key_press(Keys.Backspace.value, char)
                        elif ord(char) == 10:  # Enter
                            self._on_key_press(Keys.Enter.value, char)
                        elif ord(char) == 9:  # Tab
                            self._on_key_press(Keys.Tab.value, char)
                        elif ord(char) < 32:  # Other control characters
                            # Map control characters to their key names
                            control_key = f"ctrl+{chr(ord(char) + 64).lower()}"
                            self._on_key_press(control_key, None)
                        else:
                            self._on_key_press(char, char)

                except IOError:
                    pass
        finally:
            pass
