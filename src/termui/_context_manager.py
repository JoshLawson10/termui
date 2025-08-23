from contextvars import ContextVar
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from termui.app import App
    from termui.input import InputHandler
    from termui.logger import Logger
    from termui.renderer import Renderer


_app: ContextVar["App"] = ContextVar("app")
app: "App" = _app.get()

_input_handler: ContextVar["InputHandler"] = ContextVar("input_handler")
input_handler: "InputHandler" = _input_handler.get()

_renderer: ContextVar["Renderer"] = ContextVar("renderer")
renderer: "Renderer" = _renderer.get()

_logger: ContextVar["Logger"] = ContextVar("logger")
log: "Logger" = _logger.get()
