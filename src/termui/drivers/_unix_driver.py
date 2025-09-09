import asyncio
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
        self._input_task = None

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
        # Cancel input task if running
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()

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
        if self._loop:
            # Schedule the async input reading
            self._input_task = asyncio.run_coroutine_threadsafe(
                self._async_input_reader(), self._loop
            )

    async def _async_input_reader(self):
        """Async input reader that runs in the event loop."""
        buffer = ""

        while self._running:
            try:
                # Use select to check if there's input available
                r, _, _ = select.select([sys.stdin], [], [], 0.01)
                if not r:
                    await asyncio.sleep(0.001)
                    continue

                # Read available input
                try:
                    char = sys.stdin.read(1)
                    if not char:
                        await asyncio.sleep(0.001)
                        continue

                    # Handle escape sequences
                    if char == "\x1b":
                        buffer = char
                        # Read more characters with a short timeout
                        for _ in range(10):  # Max sequence length
                            r, _, _ = select.select([sys.stdin], [], [], 0.005)
                            if not r:
                                break
                            next_char = sys.stdin.read(1)
                            if not next_char:
                                break
                            buffer += next_char
                            # Stop if we have a complete sequence
                            if (
                                buffer.endswith(("~", "M", "m"))
                                or len(buffer) > 1
                                and buffer[-1].isalpha()
                            ):
                                break

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
                            if ord(char) == 3:  # Ctrl+C
                                self._on_key_press("ctrl+c", None)
                            else:
                                control_key = f"ctrl+{chr(ord(char) + 64).lower()}"
                                self._on_key_press(control_key, None)
                        else:
                            self._on_key_press(char, char)

                except (IOError, OSError):
                    pass

            except Exception as e:
                # Log error but don't crash the input loop
                if self._loop:
                    print(f"Input error: {e}", file=sys.stderr)

            await asyncio.sleep(0.001)

    def _run(self):
        """Main loop running in a separate thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # Start input reading
        self.read_input()

        # Run the event loop
        try:
            self._loop.run_forever()
        except Exception as e:
            print(f"Driver loop error: {e}", file=sys.stderr)
        finally:
            # Clean up
            if not self._loop.is_closed():
                self._loop.close()
