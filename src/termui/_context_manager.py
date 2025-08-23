from contextvars import ContextVar
from typing import TYPE_CHECKING

from termui.input import InputHandler
from termui.logger import Logger
from termui.renderer import Renderer


if TYPE_CHECKING:
    from termui.app import App


_app: ContextVar["App"] = ContextVar("app")
app: App = _app.get()

_input_handler: ContextVar["InputHandler"] = ContextVar(
    "input_handler", default=InputHandler()
)
input_handler: InputHandler = _input_handler.get()

_renderer: ContextVar["Renderer"] = ContextVar("renderer", default=Renderer())
renderer: Renderer = _renderer.get()

_logger: ContextVar[Logger] = ContextVar("logger", default=Logger("logs/log.txt"))
log: Logger = _logger.get()
