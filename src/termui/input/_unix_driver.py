from __future__ import annotations

import asyncio
import os
import selectors
import shutil
import signal
import sys
import termios
import tty
from codecs import getincrementaldecoder
from threading import Event, Thread
from typing import Any, TYPE_CHECKING

from termui import events
from termui._xterm_parser import XTermParser
from termui.driver import Driver
from termui.input._writer_thread import WriterThread
from termui.message import Message
from termui.messages import InBandWindowResize
from termui.utils.geometry import Size
from termui.utils.iter import loop_last


if TYPE_CHECKING:
    from termui.app import App


class SignalResume(events.Event):
    """Event sent to the app when a resume signal should be published."""


class UnixDriver(Driver):
    """Powers display and input for Linux / MacOS"""

    def __init__(
        self,
        app: App,
        *,
        debug: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
    ) -> None:
        """Initialize Linux driver.

        Args:
            app: The App instance.
            debug: Enable debug mode.
            mouse: Enable mouse support.
            size: Initial size of the terminal or `None` to detect.
        """
        super().__init__(app, debug=debug, mouse=mouse, size=size)
        self._file = sys.stderr
        self.fileno = sys.stdin.fileno()
        self.input_tty = sys.stdin.isatty()
        self.attrs_before: list[Any] | None = None
        self.exit_event = Event()
        self._key_thread: Thread | None = None
        self._writer_thread: WriterThread | None = None

        self._must_signal_resume = False
        self._in_band_window_resize = False
        self._mouse_pixels = False

        signal.signal(signal.SIGTSTP, self._sigtstp_application)
        signal.signal(signal.SIGCONT, self._sigcont_application)

    def _sigtstp_application(self, *_) -> None:
        """Handle a SIGTSTP signal."""
        if self._auto_restart:
            self.suspend_application_mode()
            self._must_signal_resume = True
        os.kill(os.getpid(), signal.SIGSTOP)

    def _sigcont_application(self, *_) -> None:
        """Handle a SICONT application."""
        if self._auto_restart:
            self.resume_application_mode()

    @property
    def can_suspend(self) -> bool:
        """Can this driver be suspended?"""
        return True

    def _get_terminal_size(self) -> tuple[int, int]:
        """Detect the terminal size.

        Returns:
            The size of the terminal as a tuple of (WIDTH, HEIGHT).
        """
        width: int | None = 80
        height: int | None = 25

        try:
            width, height = shutil.get_terminal_size()
        except (AttributeError, ValueError, OSError):
            try:
                width, height = shutil.get_terminal_size()
            except (AttributeError, ValueError, OSError):
                pass
        width = width or 80
        height = height or 25
        return width, height

    def _enable_mouse_support(self) -> None:
        """Enable reporting of mouse events."""
        if not self._mouse:
            return

        write = self.write
        write("\x1b[?1000h")
        write("\x1b[?1003h")
        write("\x1b[?1015h")
        write("\x1b[?1006h")

        self.flush()

    def _enable_mouse_pixels(self) -> None:
        """Enable mouse reporting as pixels."""
        if not self._mouse:
            return
        self.write("\x1b[?1016h")
        self._mouse_pixels = True

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.write("\x1b[?2004h")

    def _query_in_band_window_resize(self) -> None:
        self.write("\x1b[?2048$p")

    def _enable_in_band_window_resize(self) -> None:
        self.write("\x1b[?2048h")

    def _enable_line_wrap(self) -> None:
        self.write("\x1b[?7h")

    def _disable_line_wrap(self) -> None:
        self.write("\x1b[?7l")

    def _disable_in_band_window_resize(self) -> None:
        if self._in_band_window_resize:
            self.write("\x1b[?2048l")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.write("\x1b[?2004l")

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

    def write(self, data: str) -> None:
        """Write data to the output device.

        Args:
            data: Raw data.
        """
        assert self._writer_thread is not None, "Driver must be in application mode"
        self._writer_thread.write(data)

    def start_application_mode(self):
        """Start application mode."""

        def _stop_again(*_) -> None:
            """Signal handler that will put the application back to sleep."""
            os.kill(os.getpid(), signal.SIGSTOP)

        if os.isatty(self.fileno):
            signal.signal(signal.SIGTTOU, _stop_again)
            signal.signal(signal.SIGTTIN, _stop_again)
            try:
                termios.tcsetattr(
                    self.fileno, termios.TCSANOW, termios.tcgetattr(self.fileno)
                )
            except termios.error:
                return
            finally:
                signal.signal(signal.SIGTTOU, signal.SIG_DFL)
                signal.signal(signal.SIGTTIN, signal.SIG_DFL)

        loop = asyncio.get_running_loop()

        def send_size_event() -> None:
            terminal_size = self._get_terminal_size()
            width, height = terminal_size
            textual_size = Size(width, height)
            event = events.Resize(textual_size, textual_size)
            self.send_message(event)

        self._writer_thread = WriterThread(self._file)
        self._writer_thread.start()

        def on_terminal_resize(signum, stack) -> None:
            if not self._in_band_window_resize:
                send_size_event()

        signal.signal(signal.SIGWINCH, on_terminal_resize)

        self.write("\x1b[?1049h")

        self._enable_mouse_support()
        try:
            self.attrs_before = termios.tcgetattr(self.fileno)
        except termios.error:
            self.attrs_before = None

        try:
            newattr = termios.tcgetattr(self.fileno)
        except termios.error:
            pass
        else:
            newattr[tty.LFLAG] = self._patch_lflag(newattr[tty.LFLAG])
            newattr[tty.IFLAG] = self._patch_iflag(newattr[tty.IFLAG])
            newattr[tty.CC][termios.VMIN] = 1

            try:
                termios.tcsetattr(self.fileno, termios.TCSANOW, newattr)
            except termios.error:
                pass

        self.write("\x1b[?25l")
        self.write("\x1b[?1004h")
        self.write("\x1b[>1u")

        self.flush()
        self._key_thread = Thread(target=self._run_input_thread, name="textual-input")
        send_size_event()
        self._key_thread.start()
        self._request_terminal_sync_mode_support()
        self._query_in_band_window_resize()
        self._enable_bracketed_paste()
        self._disable_line_wrap()
        self._enable_mouse_support()

        if self._must_signal_resume:
            self._must_signal_resume = False
            coro = self._app.post_message(SignalResume())
            if coro is not None:
                asyncio.run_coroutine_threadsafe(
                    coro,
                    loop=loop,
                )

    def _request_terminal_sync_mode_support(self) -> None:
        """Writes an escape sequence to query the terminal support for the sync protocol."""
        if not self.input_tty:
            return
        if os.environ.get("TERM_PROGRAM", "") != "Apple_Terminal":
            self.write("\033[?2026$p")
            self.flush()

    @classmethod
    def _patch_lflag(cls, attrs: int) -> int:
        """Patch termios lflag.

        Args:
            attributes: New set attributes.

        Returns:
            New lflag.

        """
        ISIG = 0 if os.environ.get("TEXTUAL_ALLOW_SIGNALS") else termios.ISIG

        return attrs & ~(termios.ECHO | termios.ICANON | termios.IEXTEN | ISIG)

    @classmethod
    def _patch_iflag(cls, attrs: int) -> int:
        return attrs & ~(
            termios.IXON | termios.IXOFF | termios.ICRNL | termios.INLCR | termios.IGNCR
        )

    def disable_input(self) -> None:
        """Disable further input."""
        try:
            if not self.exit_event.is_set():
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)
                self._disable_mouse_support()
                self.exit_event.set()
                if self._key_thread is not None:
                    self._key_thread.join()
                self.exit_event.clear()
                try:
                    termios.tcflush(self.fileno, termios.TCIFLUSH)
                except termios.error:
                    pass
        except Exception:
            pass

    def stop_application_mode(self) -> None:
        """Stop application mode, restore state."""
        self._disable_bracketed_paste()
        self._enable_line_wrap()
        self._disable_in_band_window_resize()
        self.disable_input()

        if self.attrs_before is not None:
            try:
                termios.tcsetattr(self.fileno, termios.TCSANOW, self.attrs_before)
            except termios.error:
                pass

        self.write("\x1b[<u")
        self.write("\x1b[?1049l")
        self.write("\x1b[?25h")
        self.write("\x1b[?1004l")
        self.flush()

    def close(self) -> None:
        """Perform cleanup."""
        if self._writer_thread is not None:
            self._writer_thread.stop()

    def _run_input_thread(self) -> None:
        """
        Key thread target that wraps run_input_thread() to die gracefully if it raises
        an exception
        """
        try:
            self.run_input_thread()
        except BaseException:
            pass

    def run_input_thread(self) -> None:
        """Wait for input and dispatch events."""
        selector = selectors.SelectSelector()
        selector.register(self.fileno, selectors.EVENT_READ)

        fileno = self.fileno
        EVENT_READ = selectors.EVENT_READ

        parser = XTermParser(self._debug)
        feed = parser.feed
        tick = parser.tick

        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder
        read = os.read

        def process_selector_events(
            selector_events: list[tuple[selectors.SelectorKey, int]],
            final: bool = False,
        ) -> None:
            """Process events from selector.

            Args:
                selector_events: List of selector events.
                final: True if this is the last call.

            """
            for last, (_selector_key, mask) in loop_last(selector_events):
                if mask & EVENT_READ:
                    unicode_data = decode(read(fileno, 1024 * 4), final=final and last)
                    if not unicode_data:
                        break
                    for event in feed(unicode_data):
                        self.process_message(event)
            for event in tick():
                self.process_message(event)

        try:
            while not self.exit_event.is_set():
                process_selector_events(selector.select(0.1))
            selector.unregister(self.fileno)
            process_selector_events(selector.select(0.1), final=True)

        finally:
            selector.close()

    def process_message(self, message: Message) -> None:
        if isinstance(message, InBandWindowResize):
            if message.supported:
                self._in_band_window_resize = True
                if message.enabled:
                    super().process_message(message)
                else:
                    self._enable_in_band_window_resize()
                    super().process_message(InBandWindowResize(True, True))
                self._enable_mouse_pixels()
                return

        super().process_message(message)
