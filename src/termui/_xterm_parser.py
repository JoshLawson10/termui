from __future__ import annotations

import os
import re
from collections import deque
from time import perf_counter
from typing import (
    Callable,
    Deque,
    Final,
    Generator,
    Generic,
    Iterable,
    NamedTuple,
    TypeVar,
)

from termui import constants, events, messages
from termui._ansi import ANSI_SEQUENCES_KEYS, IGNORE_SEQUENCE
from termui._context_manager import log
from termui.keys import _character_to_key, FUNCTIONAL_KEYS, KEY_NAME_REPLACEMENTS, Keys
from termui.message import Message
from termui.utils.geometry import Size

# When trying to determine whether the current sequence is a supported/valid
# escape sequence, at which length should we give up and consider our search
# to be unsuccessful?
_MAX_SEQUENCE_SEARCH_THRESHOLD = 32

_re_mouse_event = re.compile("^" + re.escape("\x1b[") + r"(<?[-\d;]+[mM]|M...)\Z")
_re_terminal_mode_response = re.compile(
    "^" + re.escape("\x1b[") + r"\?(?P<mode_id>\d+);(?P<setting_parameter>\d)\$y"
)

_re_cursor_position = re.compile(r"\x1b\[(?P<row>\d+);(?P<col>\d+)R")

BRACKETED_PASTE_START: Final[str] = "\x1b[200~"
"""Sequence received when a bracketed paste event starts."""
BRACKETED_PASTE_END: Final[str] = "\x1b[201~"
"""Sequence received when a bracketed paste event ends."""
FOCUSIN: Final[str] = "\x1b[I"
"""Sequence received when the terminal receives focus."""
FOCUSOUT: Final[str] = "\x1b[O"
"""Sequence received when focus is lost from the terminal."""

SPECIAL_SEQUENCES = {BRACKETED_PASTE_START, BRACKETED_PASTE_END, FOCUSIN, FOCUSOUT}
"""Set of special sequences."""

_re_extended_key: Final = re.compile(r"\x1b\[(?:(\d+)(?:;(\d+))?)?([u~ABCDEFHPQRS])")
_re_in_band_window_resize: Final = re.compile(
    r"\x1b\[48;(\d+(?:\:.*?)?);(\d+(?:\:.*?)?);(\d+(?:\:.*?)?);(\d+(?:\:.*?)?)t"
)


IS_ITERM = (
    os.environ.get("LC_TERMINAL", "") == "iTerm2"
    or os.environ.get("TERM_PROGRAM", "") == "iTerm.app"
)


class ParseError(Exception):
    """Base class for parse related errors."""


class ParseEOF(ParseError):
    """End of Stream."""


class ParseTimeout(ParseError):
    """Read has timed out."""


class Read1(NamedTuple):
    """Reads a single character."""

    timeout: float | None = None
    """Optional timeout in seconds."""


class Peek1(NamedTuple):
    """Reads a single character, but does not advance the parser position."""

    timeout: float | None = None
    """Optional timeout in seconds."""


T = TypeVar("T")
TokenCallback = Callable[[T], None]


class Parser(Generic[T]):
    """Base class for a simple parser."""

    read1 = Read1
    peek1 = Peek1

    def __init__(self) -> None:
        self._eof = False
        self._tokens: Deque[T] = deque()
        self._gen = self.parse(self._tokens.append)
        self._awaiting: Read1 | Peek1 = next(self._gen)
        self._timeout_time: float | None = None

    def get_time(self) -> float:
        """Get the current time in seconds since the epoch."""
        return perf_counter()

    @property
    def is_eof(self) -> bool:
        """Is the parser at the end of the file (i.e. exhausted)?"""
        return self._eof

    def tick(self) -> Iterable[T]:
        """Call at regular intervals to check for timeouts."""
        if self._timeout_time is not None and self.get_time() >= self._timeout_time:
            self._timeout_time = None
            self._awaiting = self._gen.throw(ParseTimeout())
            while self._tokens:
                yield self._tokens.popleft()

    def feed(self, data: str) -> Iterable[T]:
        """Feed data to be parsed.

        Args:
            data: Data to parser.

        Raises:
            ParseError: If the data could not be parsed.

        Yields:
            T: A generic data type.
        """
        if self._eof:
            raise ParseError("end of file reached") from None

        if not data:
            self._eof = True
            try:
                self._gen.throw(ParseEOF())
            except StopIteration:
                pass
            while self._tokens:
                yield self._tokens.popleft()
            return

        pos = 0
        while self._tokens:
            yield self._tokens.popleft()

        while pos < len(data):
            if isinstance(self._awaiting, Read1):
                self._timeout_time = None
                self._awaiting = self._gen.send(data[pos])
                pos += 1
            elif isinstance(self._awaiting, Peek1):
                self._timeout_time = None
                self._awaiting = self._gen.send(data[pos])

            if self._awaiting.timeout is not None:
                self._timeout_time = self.get_time() + self._awaiting.timeout

            while self._tokens:
                yield self._tokens.popleft()

    def parse(
        self, token_callback: TokenCallback
    ) -> Generator[Read1 | Peek1, str, None]:
        """Implement to parse a stream of text.

        Args:
            token_callback: Callable to report a successful parsed data type.

        Yields:
            ParseAwaitable: One of `self.read1` or `self.peek1`
        """
        yield from ()


class XTermParser(Parser[Message]):
    """Parser for xterm mouse events."""

    _re_sgr_mouse = re.compile(r"\x1b\[<(\d+);(-?\d+);(-?\d+)([Mm])")

    def __init__(self, debug: bool = False) -> None:
        self.last_x = 0.0
        self.last_y = 0.0
        self.mouse_pixels = False
        self.terminal_size: Size | None = None
        self.terminal_pixel_size: Size | None = None
        self.debug = debug
        super().__init__()

    def debug_log(self, message: str) -> None:
        """Log a debug message.

        Args:
            message: The debug message to log.
        """
        if self.debug:
            log.debug(message)

    def feed(self, data: str) -> Iterable[Message]:
        """Feed data to the parser.

        Args:
            data: The data to feed to the parser.
        """
        self.debug_log(f"FEED {data!r}")
        return super().feed(data)

    def parse_mouse_code(self, code: str) -> Message | None:
        """Parse a mouse event code.

        Args:
            code: The mouse event code to parse.
        """
        sgr_match = self._re_sgr_mouse.match(code)
        if sgr_match:
            _buttons, _x, _y, state = sgr_match.groups()
            buttons = int(_buttons)
            x = float(int(_x) - 1)
            y = float(int(_y) - 1)
            if x < 0 or y < 0:
                return None
            if (
                self.mouse_pixels
                and self.terminal_pixel_size is not None
                and self.terminal_size is not None
            ):
                pixel_width, pixel_height = self.terminal_pixel_size
                width, height = self.terminal_size
                x_ratio = pixel_width / width
                y_ratio = pixel_height / height
                x /= x_ratio
                y /= y_ratio
            self.last_x = x
            self.last_y = y
            event_class: type[events.MouseEvent]

            if buttons & 64:
                event_class = [
                    events.MouseScrollUp,
                    events.MouseScrollDown,
                    events.MouseScrollLeft,
                    events.MouseScrollRight,
                ][buttons & 3]
                button = 0
            else:
                button = (buttons + 1) & 3
                # XTerm events for mouse movement can look like mouse button down events. But if there is no key pressed,
                # it's a mouse move event.
                if buttons & 32 or button == 0:
                    event_class = events.MouseMove
                else:
                    event_class = events.MouseDown if state == "M" else events.MouseUp

            event = event_class(
                None,
                x,
                y,
                button,
            )
            return event
        return None

    def parse(
        self, token_callback: TokenCallback
    ) -> Generator[Read1 | Peek1, str, None]:
        """Parse the input stream and yield tokens.

        Args:
            token_callback: The callback to invoke with each token.
        """
        ESC = "\x1b"
        read1 = self.read1
        sequence_to_key_events = self._sequence_to_key_events
        paste_buffer: list[str] = []
        bracketed_paste = False

        def on_token(token: Message) -> None:
            """Hook to log events."""
            self.debug_log(str(token))
            if isinstance(token, events.Resize):
                self.terminal_size = token.size
                self.terminal_pixel_size = token.pixel_size
            token_callback(token)

        def on_key_token(event: events.Key) -> None:
            """Token callback wrapper for handling keys.

            Args:
                event: The key event to send to the callback.

            This wrapper looks for keys that should be ignored, and filters
            them out, logging the ignored sequence when it does.
            """
            if event.key == Keys.Ignore:
                self.debug_log(f"ignored={event.character!r}")
            else:
                on_token(event)

        def reissue_sequence_as_keys(reissue_sequence: str) -> None:
            """Called when an escape sequence hasn't been understood.

            Args:
                reissue_sequence: Key sequence to report to the app.
            """
            if reissue_sequence:
                self.debug_log(f"REISSUE {repr(reissue_sequence)}")
                for character in reissue_sequence:
                    key_events = sequence_to_key_events(character)
                    for event in key_events:
                        if event.key == "escape":
                            event = events.Key("circumflex_accent")
                        on_token(event)

        while not self.is_eof:
            if not bracketed_paste and paste_buffer:
                pasted_text = "".join(paste_buffer[:-1])
                on_token(events.Paste(pasted_text.replace("\x00", "")))
                paste_buffer.clear()

            try:
                character = yield read1()
            except ParseEOF:
                return

            if bracketed_paste:
                paste_buffer.append(character)

            self.debug_log(f"character={character!r}")
            if character != ESC:
                if not bracketed_paste:
                    for event in sequence_to_key_events(character):
                        on_key_token(event)
                if not character:
                    return
                continue

            sequence: str = ESC

            def send_escape() -> None:
                """Send escape key and reissue sequence."""
                on_token(events.Key("escape", "\x1b"))
                reissue_sequence_as_keys(sequence[1:])

            while True:
                try:
                    new_character = yield read1(constants.ESCAPE_DELAY)
                except ParseTimeout:
                    send_escape()
                    break
                except ParseEOF:
                    send_escape()
                    return

                if new_character == ESC:
                    send_escape()
                    sequence = character
                    continue

                sequence += new_character
                if len(sequence) > _MAX_SEQUENCE_SEARCH_THRESHOLD:
                    reissue_sequence_as_keys(sequence)
                    break

                self.debug_log(f"sequence={sequence!r}")
                if sequence in SPECIAL_SEQUENCES:
                    if sequence == BRACKETED_PASTE_START:
                        bracketed_paste = True

                    if sequence == BRACKETED_PASTE_END:
                        bracketed_paste = False
                    break
                if match := _re_in_band_window_resize.fullmatch(sequence):
                    height, width, _, _ = [
                        group.partition(":")[0] for group in match.groups()
                    ]
                    resize_event = events.Resize.from_dimensions(
                        (int(width), int(height)),
                    )

                    self.terminal_size = resize_event.size
                    self.terminal_pixel_size = resize_event.pixel_size
                    self.mouse_pixels = True
                    on_token(resize_event)
                    break

                if not bracketed_paste:
                    # Check cursor position report
                    cursor_position_match = _re_cursor_position.match(sequence)
                    if cursor_position_match is not None:
                        row, column = map(int, cursor_position_match.groups())
                        x = int(column) - 1
                        y = int(row) - 1
                        on_token(events.CursorPosition(x, y))
                        break

                    # Was it a pressed key event that we received?
                    key_events = list(sequence_to_key_events(sequence))
                    for key_event in key_events:
                        on_key_token(key_event)
                    if key_events:
                        break
                    # Or a mouse event?
                    mouse_match = _re_mouse_event.match(sequence)
                    if mouse_match is not None:
                        mouse_code = mouse_match.group(0)
                        mouse_event = self.parse_mouse_code(mouse_code)
                        if mouse_event is not None:
                            on_token(mouse_event)
                        break

                    # Or a mode report?
                    # (i.e. the terminal saying it supports a mode we requested)
                    mode_report_match = _re_terminal_mode_response.match(sequence)
                    if mode_report_match is not None:
                        mode_id = mode_report_match["mode_id"]
                        setting_parameter = int(mode_report_match["setting_parameter"])
                        if mode_id == "2026" and setting_parameter > 0:
                            on_token(messages.TerminalSupportsSynchronizedOutput())
                        elif mode_id == "2048" and not IS_ITERM:
                            in_band_event = (
                                messages.InBandWindowResize.from_setting_parameter(
                                    setting_parameter
                                )
                            )
                            on_token(in_band_event)
                        break

    def _sequence_to_key_events(self, sequence: str) -> Iterable[events.Key]:
        """Map a sequence of code points on to a sequence of keys.

        Args:
            sequence: Sequence of code points.

        Returns:
            Keys
        """

        if (match := _re_extended_key.fullmatch(sequence)) is not None:
            number, modifiers, end = match.groups()
            number = number or 1
            if not (key := FUNCTIONAL_KEYS.get(f"{number}{end}", "")):
                try:
                    key = _character_to_key(chr(int(number)))
                except Exception:
                    key = chr(int(number))
            key_tokens: list[str] = []
            if modifiers:
                modifier_bits = int(modifiers) - 1
                MODIFIERS = ("shift", "alt", "ctrl", "super", "hyper", "meta")
                for bit, modifier in enumerate(MODIFIERS):
                    if modifier_bits & (1 << bit):
                        key_tokens.append(modifier)

            key_tokens.sort()
            key_tokens.append(key)
            yield events.Key(
                "+".join(key_tokens), sequence if len(sequence) == 1 else None
            )
            return

        keys = ANSI_SEQUENCES_KEYS.get(sequence)
        # If we're being asked to ignore the key...
        if keys is IGNORE_SEQUENCE:
            # ...build a special ignore key event, which has the ignore
            # name as the key (that is, the key this sequence is bound
            # to is the ignore key) and the sequence that was ignored as
            # the character.
            yield events.Key(Keys.Ignore, sequence)
            return
        if isinstance(keys, tuple):
            # If the sequence mapped to a tuple, then it's values from the
            # `Keys` enum. Raise key events from what we find in the tuple.
            for key in keys:
                yield events.Key(key.value, sequence if len(sequence) == 1 else None)
            return
        # If keys is a string, the intention is that it's a mapping to a
        # character, which should really be treated as the sequence for the
        # purposes of the next step...
        if isinstance(keys, str):
            sequence = keys
        # If the sequence is a single character, attempt to process it as a
        # key.
        if len(sequence) == 1:
            try:
                if not sequence.isalnum():
                    name = _character_to_key(sequence)
                else:
                    name = sequence
                name = KEY_NAME_REPLACEMENTS.get(name, name)
                yield events.Key(name, sequence)
            except Exception:
                yield events.Key(sequence, sequence)
