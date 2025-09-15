import os
from typing import Final

_get_environ = os.environ.get


def _get_environ_bool(name: str) -> bool:
    """Check an environment variable switch.

    Args:
        name: Name of environment variable.

    Returns:
        `True` if the env var is "1", otherwise `False`.
    """
    return _get_environ(name) == "1"


def _get_environ_int(
    name: str, default: int, minimum: int | None = None, maximum: int | None = None
) -> int:
    """Retrieves an integer environment variable.

    Args:
        name: Name of environment variable.
        default: The value to use if the value is not set, or set to something other
            than a valid integer.
        minimum: Optional minimum value.

    Returns:
        The integer associated with the environment variable if it's set to a valid int
            or the default value otherwise.
    """
    try:
        value = int(os.environ[name])
    except KeyError:
        return default
    except ValueError:
        return default
    if minimum is not None:
        return max(minimum, value)
    if maximum is not None:
        return min(maximum, value)
    return value


DEBUG: Final[bool] = _get_environ_bool("TERMUI_DEBUG")
"""Enable debug mode."""

LOG_FILE: Final[str] = _get_environ("TERMUI_LOG_FILE", None)
"""Log file to be used by the logger."""

DEFAULT_THEME: Final[str] = _get_environ("TEXTUAL_THEME", "textual-dark")
"""Default theme to be used in the app."""
