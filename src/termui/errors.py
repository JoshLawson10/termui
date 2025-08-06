class AlignmentError(Exception):
    """Base class for all alignment errors."""

    pass


class DimensionError(Exception):
    """Base class for all size-related errors."""

    pass


class AppError(Exception):
    """Base class for all application-related errors."""

    pass


class ScreenError(Exception):
    """Base class for all screen-related errors."""

    pass


class WidgetError(Exception):
    """Base class for all widget-related errors."""

    pass


class RenderError(Exception):
    """Base class for all rendering-related errors."""

    pass


class AsyncError(Exception):
    """Base class for all asynchronous operation errors."""

    pass
