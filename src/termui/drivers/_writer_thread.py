from __future__ import annotations

import fcntl
import os
import threading
from queue import Queue
from typing import IO, Final

MAX_QUEUED_WRITES: Final[int] = 64


class WriterThread(threading.Thread):
    """A thread / file-like to do writes to stdout in the background."""

    def __init__(self, file: IO[str]) -> None:
        super().__init__(daemon=True, name="TERMUI_OUTPUT")
        self._queue: Queue[str | None] = Queue(MAX_QUEUED_WRITES)
        self._file = file

        fd = file.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)

    def write(self, text: str) -> None:
        """Write text. Text will be enqueued for writing.

        Args:
            text: Text to write to the file.
        """
        self._queue.put(text)

    @staticmethod
    def isatty() -> bool:
        """Pretend to be a terminal.

        Returns:
            True.
        """
        return True

    def fileno(self) -> int:
        """Get file handle number.

        Returns:
            File number of proxied file.
        """
        return self._file.fileno()

    def flush(self) -> None:
        """Flush the file (a no-op, because flush is done in the thread)."""
        return

    def run(self) -> None:
        while True:
            text: str | None = self._queue.get()
            if text is None:
                break
            data = text.encode()
            while data:
                try:
                    written = os.write(self.fileno(), data)
                    data = data[written:]
                except BlockingIOError:
                    threading.Event().wait(0.01)
            if self._queue.qsize() == 0:
                self._file.flush()
        self._file.flush()

    def stop(self) -> None:
        """Stop the thread, and block until it finished."""
        self._queue.put(None)
        self.join()
