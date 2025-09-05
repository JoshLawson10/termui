from __future__ import annotations

import os
from typing import Final

get_environ = os.environ.get


def _get_environ_bool(name: str) -> bool:
    """Check an environment variable switch.

    Args:
        name: Name of environment variable.

    Returns:
        `True` if the env var is "1", otherwise `False`.
    """
    has_environ = get_environ(name) == "1"
    return has_environ


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


DEBUG: Final[bool] = _get_environ_bool("DEBUG")
"""Enable debug mode."""

DRIVER: Final[str | None] = get_environ("DRIVER", None)
"""Import for replacement driver."""

LOG_FILE: Final[str | None] = get_environ("LOG_FILE", None)
"""A last resort log file that appends all logs, when devtools isn't working."""

MAX_FPS: Final[int] = _get_environ_int("MAX_FPS", 60, minimum=1)
"""Maximum frames per second for updates."""

ESCAPE_DELAY: Final[float] = _get_environ_int("ESCDELAY", 100, minimum=1) / 1000.0
"""The delay (in seconds) before reporting an escape key (not used if the extend key protocol is available)."""
