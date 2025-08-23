from contextvars import ContextVar
from typing import TYPE_CHECKING

from termui.logger import Logger


if TYPE_CHECKING:
    from termui.app import App
    from termui.screen import Screen

current_app: ContextVar["App"] = ContextVar("current_app")
current_screen: ContextVar["Screen"] = ContextVar("current_screen")

_logger: ContextVar[Logger] = ContextVar("logger", default=Logger("logs/log.txt"))
log: Logger = _logger.get()
