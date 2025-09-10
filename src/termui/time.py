from time import perf_counter


def get_time() -> float:
    """Get the current time in seconds since the epoch."""
    return perf_counter()
