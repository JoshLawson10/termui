import asyncio
import fcntl
import os
import select
import sys
import termios
import tty

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
        self.write("\x1b[?1006h")  # Enable SGR mouse mode
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
        self.write("\x1b[?1006l")  # Disable SGR mouse mode
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
        while self._running:
            try:
                # Tick the parser to handle any timeouts
                self._tick_parser()

                # Use select to check if there's input available
                r, _, _ = select.select([sys.stdin], [], [], 0.01)
                if not r:
                    await asyncio.sleep(0.001)
                    continue

                try:
                    # Read available input data in chunks
                    data = sys.stdin.read(1024)
                    if not data:
                        await asyncio.sleep(0.001)
                        continue

                    # Feed the data directly to the parser
                    self._process_parser_events(data)

                except (IOError, OSError):
                    pass

            except Exception as e:
                # Log error but don't crash the input loop
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
