import asyncio
import shutil
import sys
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from termui import events
from termui.drivers._keybind_manager import KeybindManager
from termui.drivers._parser import Parser
from termui.drivers._writer_thread import WriterThread
from termui.keybind import Keybind
from termui.logger import log


class Driver(ABC):
    """Base class for all platform-specific I/O drivers."""

    def __init__(self):
        self.event_queue: asyncio.Queue[events.Event] = asyncio.Queue()
        """Queue for input events."""
        self._running: bool = False
        """Whether the driver is running."""
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        """Reference to the async loop."""
        self._thread: Optional[threading.Thread] = None
        """Thread to start the input manager in."""
        self._file = sys.stdout
        """Reference to STDOUT."""
        self._writer_thread: Optional[WriterThread] = None
        """Reference to the file writing thread."""
        self.keybind_manager: KeybindManager = KeybindManager()
        """Manager for handling key bindings."""
        self._parser: Parser[events.Event] = Parser()
        """The ANSI parser for handling input sequences."""

        log.system("I/O Driver Initialised")

    def register_keybind(self, keybind: Keybind) -> None:
        """Register a keybind with the input manager.

        Args:
            keybind (Keybind): The keybind to register.
        """
        self.keybind_manager.register_keybind(keybind)

    def register_keybinds_from_object(self, obj: Any) -> None:
        """Register keybinds from an object's methods with @keybind decorator.

        Args:
            obj (Any): The object to register keybinds from.
        """
        self.keybind_manager.register_keybinds_from_object(obj)

    @staticmethod
    def get_terminal_size() -> tuple[int, int]:
        """Get the current size of the terminal.

        Returns:
            A tuple containing the width and height of the terminal.
        """
        size = shutil.get_terminal_size(fallback=(80, 24))
        return size.columns, size.lines

    @abstractmethod
    def setup(self) -> None:
        """Setup the input manager."""

    @abstractmethod
    def teardown(self) -> None:
        """Tear down the input manager."""

    @abstractmethod
    def read_input(self) -> None:
        """Read input from the device."""

    def start(self) -> None:
        """Starts the input manager in a new thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        time.sleep(0.01)

        self._writer_thread = WriterThread(self._file)
        self._writer_thread.start()
        self.setup()

        log.system("I/O Driver Started")

    def stop(self) -> None:
        """Stops the input manager."""
        if not self._running:
            return
        self._running = False
        self.teardown()
        self.write("\033[H\033[J")  # Clear the screen

        if self._loop and not self._loop.is_closed():
            try:
                self._loop.call_soon_threadsafe(self._loop.stop)
            except RuntimeError:
                pass  # Loop may already be stopped

        if self._thread:
            self._thread.join(timeout=1.0)

        if self._writer_thread:
            self._writer_thread.stop()

        log.system("I/O Driver Terminated")

    def write(self, data: str) -> None:
        """Writes text to the output.

        Args:
            data (str): The text to write.
        """
        if self._writer_thread is not None:
            self._writer_thread.write(data)

    def flush(self) -> None:
        """Flush the output."""
        if self._writer_thread is not None:
            self._writer_thread.flush()

    async def get_event(self) -> events.Event:
        """Asynchronously gets an event from the queue.

        Returns:
            events.Event: The event from the queue.
        """
        return await self.event_queue.get()

    def _put_event(self, event: events.Event) -> None:
        """Puts an event into the asyncio queue from the listener thread.

        Args:
            event (events.Event): The event to put into the queue.
        """
        if self._loop and self._loop.is_running():
            try:
                # Handle Key events through keybind manager
                if isinstance(event, events.Key):
                    keybind_triggered = self.keybind_manager.handle_key_event(event)
                    # Only put the event in the queue if no keybind was triggered
                    if not keybind_triggered:
                        asyncio.run_coroutine_threadsafe(
                            self.event_queue.put(event), self._loop
                        )
                else:
                    # Non-key events go straight to the queue
                    asyncio.run_coroutine_threadsafe(
                        self.event_queue.put(event), self._loop
                    )
            except RuntimeError as e:
                log.error(f"Failed to put event: {e}")

    def _process_parser_events(self, data: str) -> None:
        """Process input data through the parser and handle resulting events.

        Args:
            data (str): Raw input data to parse.
        """
        try:
            # Feed data to parser and get events
            events_iter = self._parser.feed(data)
            for event in events_iter:
                self._put_event(event)
        except Exception as e:
            log.error(f"Parser error: {e}")

    def _tick_parser(self) -> None:
        """Tick the parser to handle timeouts."""
        try:
            events_iter = self._parser.tick()
            for event in events_iter:
                self._put_event(event)
        except Exception as e:
            log.error(f"Parser tick error: {e}")

    def _run(self):
        """Main loop running in a separate thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            # Run the input reading
            self.read_input()

            self._loop.run_forever()
        except Exception as e:
            log.error(f"Driver thread error: {e}")
        finally:
            self.stop()
