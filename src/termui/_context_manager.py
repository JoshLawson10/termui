from contextvars import ContextVar
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from termui.app import App
    from termui.renderer import Renderer


_app: ContextVar["App"] = ContextVar("app")
_renderer: ContextVar["Renderer"] = ContextVar("renderer")


class _ContextVarProxy:
    """A simple proxy that defers .get() until accessed."""

    def __init__(self, ctx: ContextVar, name: str):
        self._ctx = ctx
        self._name = name

    def __getattr__(self, item):
        return getattr(self._ctx.get(), item)

    def __call__(self):
        """Allow direct retrieval via function call, e.g., app()"""
        return self._ctx.get()

    def __repr__(self):
        try:
            value = self._ctx.get()
        except LookupError:
            return f"<Unbound ContextVarProxy {self._name}>"
        return f"<ContextVarProxy {self._name} -> {value!r}>"


app = cast("App", _ContextVarProxy(_app, "app"))
renderer = cast("Renderer", _ContextVarProxy(_renderer, "renderer"))
