"""from functools import wraps
from typing import Callable, Any
from .keybind import Keybind


def keybind(key: str, description: str = "", visible: bool = True)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            return func(self, *args, **kwargs)

        setattr(
            wrapper,
            "_keybind",
            Keybind(key=key, action=wrapper, description=description, visible=visible),
        )

        return wrapper

    return decorator
"""
