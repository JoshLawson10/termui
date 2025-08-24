class AlignmentError(Exception):
    """Base class for all alignment errors."""


class DimensionError(Exception):
    """Base class for all size-related errors."""


class AppError(Exception):
    """Base class for all application-related errors."""


class ScreenError(Exception):
    """Base class for all screen-related errors."""


class WidgetError(Exception):
    """Base class for all widget-related errors."""


class RenderError(Exception):
    """Base class for all rendering-related errors."""


class AsyncError(Exception):
    """Base class for all asynchronous operation errors."""
