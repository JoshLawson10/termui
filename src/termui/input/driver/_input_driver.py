import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Optional

from termui import events
from termui._ansi import ANSI_SEQUENCES_KEYS, IGNORE_SEQUENCE
from termui._context_manager import log
from termui._keys import key_to_character, Keys
from termui.input import Keybind
from termui.input._keybind_manager import KeybindManager


class InputDriver(ABC):
    """Abstract base class for input managers."""

    def __init__(self):
        self.event_queue: asyncio.Queue[events.InputEvent] = asyncio.Queue()
        self._running: bool = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self.keybind_manager: KeybindManager = KeybindManager()

        # Mouse state tracking
        self._mouse_pressed: bool = False
        self._last_mouse_x: int = -1
        self._last_mouse_y: int = -1

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
        self.setup()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stops the input manager."""
        if not self._running:
            return
        self._running = False
        self.teardown()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join()

    async def get_event(self) -> events.InputEvent:
        """Asynchronously gets an event from the queue.

        Returns:
            events.InputEvent: The event from the queue.
        """
        return await self.event_queue.get()

    def _put_event(self, event: events.InputEvent) -> None:
        """Puts an event into the asyncio queue from the listener thread.

        Args:
            event (events.InputEvent): The event to put into the queue.
        """
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.event_queue.put(event), self._loop)
            log.debug(f"INPUT EVENT: {event}")

    def _on_key_press(self, key: str, character: str | None = None) -> None:
        """Handle key press events.

        Args:
            key (str): The key that was pressed.
            character (str | None): The character representation of the key.
        """
        # Convert key to Keys enum value if possible
        key_str = key
        try:
            key_enum = Keys(key)
            key_str = key_enum.value
        except ValueError:
            # If it's not a known key, use the original string
            pass

        event = events.Key(key=key_str, character=character)
        keybind_triggered = self.keybind_manager.handle_key_event(event)

        # Only put the event in the queue if no keybind was triggered
        if not keybind_triggered:
            self._put_event(event)

    def _on_key_release(self, key: str):
        """Handle key release events.

        Args:
            key (str): The key that was released.
        """
        self.keybind_manager.handle_key_release(key)

    def _on_mouse_move(self, x: int, y: int, button: int = -1) -> None:
        """Handle mouse movement events.

        Args:
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            button (int): The mouse button that was pressed.
        """
        if self._mouse_pressed:
            event = events.MouseDrag(x=x, y=y, button=button)
        else:
            event = events.MouseMove(x=x, y=y, button=button)
        self._put_event(event)

    def _on_mouse_down(self, x: int, y: int, button: int) -> None:
        """Handle mouse button down events.

        Args:
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            button (int): The mouse button that was pressed.
        """
        self._mouse_pressed = True
        self._last_mouse_x = x
        self._last_mouse_y = y
        self._put_event(events.MouseDown(x=x, y=y, button=button))

    def _on_mouse_up(self, x: int, y: int, button: int) -> None:
        """Handle mouse button up events.

        Args:
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            button (int): The mouse button that was released.
        """
        self._mouse_pressed = False
        self._put_event(events.MouseUp(x=x, y=y, button=button))

        # Check if this was a click (quick down-up)
        if self._last_mouse_x == x and self._last_mouse_y == y:
            self._put_event(events.Click(x=x, y=y, button=button))

    def _on_mouse_scroll(self, x: int, y: int, direction: str) -> None:
        """Handle mouse scroll events.

        Args:
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            direction (str): The scroll direction ("up", "down", "left", "right").
        """
        match direction:
            case "up":
                self._put_event(events.MouseScrollUp(x=x, y=y))
            case "down":
                self._put_event(events.MouseScrollDown(x=x, y=y))
            case "left":
                self._put_event(events.MouseScrollLeft(x=x, y=y))
            case "right":
                self._put_event(events.MouseScrollRight(x=x, y=y))

    def _parse_ansi_sequence(self, sequence: str) -> Optional[events.InputEvent]:
        """Parse ANSI escape sequences using the provided ANSI mapping.

        Args:
            sequence (str): The ANSI escape sequence to parse.

        Returns:
            Optional[events.InputEvent]: The parsed input event, if any.
        """
        if sequence in ANSI_SEQUENCES_KEYS:
            result = ANSI_SEQUENCES_KEYS[sequence]

            if result is IGNORE_SEQUENCE:
                return None

            if isinstance(result, str):
                # Single character result
                character = key_to_character(result)
                self._on_key_press(result, character)
                return None

            if isinstance(result, tuple):
                # Multiple keys (like modifier combinations)
                for key in result:
                    character = key_to_character(key.value)
                    self._on_key_press(key.value, character)
                return None

        # Check if it's a mouse sequence
        if sequence.startswith("\x1b[") and (
            "<" in sequence or "M" in sequence or "m" in sequence
        ):
            return self._parse_mouse_sequence(sequence)

        # Unknown sequence, treat as a regular key
        character = key_to_character(sequence)
        self._on_key_press(sequence, character)
        return None

    def _parse_mouse_sequence(self, sequence: str) -> Optional[events.InputEvent]:
        """Parse mouse-related ANSI sequences.

        Args:
            sequence (str): The ANSI escape sequence to parse.

        Returns:
            Optional[events.InputEvent]: The parsed input event, if any.
        """
        if not sequence.startswith("\x1b["):
            return None

        # CSI sequence
        code = sequence[2:]

        # Mouse event parsing
        if code.startswith("<"):
            # Parse X10 mouse events: \x1b[M<btn><x><y>
            if len(code) >= 4 and code[0] == "<":
                btn = ord(code[1]) - 32
                x = ord(code[2]) - 32
                y = ord(code[3]) - 32

                button = btn & 3
                pressed = (btn & 64) == 0
                scroll = (btn & 96) == 96

                if scroll:
                    if button == 0:
                        self._on_mouse_scroll(x, y, "up")
                    elif button == 1:
                        self._on_mouse_scroll(x, y, "down")
                    elif button == 2:
                        self._on_mouse_scroll(x, y, "right")
                    elif button == 3:
                        self._on_mouse_scroll(x, y, "left")
                elif pressed:
                    self._on_mouse_down(x, y, button)
                else:
                    self._on_mouse_up(x, y, button)

                return None

        # Extended mouse event parsing (SGR mode)
        elif code.startswith("[") and ("M" in code or "m" in code):
            # Parse SGR mouse events: \x1b[<btn;x;y>M or \x1b[<btn;x;y>m
            parts = code.split(";")
            if len(parts) >= 3 and (parts[-1].endswith("M") or parts[-1].endswith("m")):
                try:
                    btn = int(parts[0][1:])  # Skip the initial '['
                    x = int(parts[1])
                    y = int(parts[2][:-1])  # Remove the trailing 'M' or 'm'

                    button = btn & 3
                    pressed = (btn & 32) == 0  # Button press vs release
                    scroll = (btn & 96) == 96  # Scroll event

                    if scroll:
                        match button:
                            case 0:
                                self._on_mouse_scroll(x, y, "up")
                            case 1:
                                self._on_mouse_scroll(x, y, "down")
                            case 2:
                                self._on_mouse_scroll(x, y, "right")
                            case 3:
                                self._on_mouse_scroll(x, y, "left")
                    elif pressed:
                        self._on_mouse_down(x, y, button)
                    else:
                        self._on_mouse_up(x, y, button)

                    return None
                except (ValueError, IndexError):
                    pass

        return None

    def _run(self):
        """Main loop running in a separate thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # Run the input reading
        self.read_input()

        self._loop.run_forever()
