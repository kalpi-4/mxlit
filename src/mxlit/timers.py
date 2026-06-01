from mxlit.context import get_context


class _AutoRefreshCtx:
    def __init__(self, trigger: str) -> None:
        self._trigger = trigger
        self._prev: str | None = None

    def __enter__(self) -> "_AutoRefreshCtx":
        ctx = get_context()
        if ctx:
            self._prev = ctx._auto_refresh
            ctx._auto_refresh = self._trigger
        return self

    def __exit__(self, *_) -> bool:
        ctx = get_context()
        if ctx:
            ctx._auto_refresh = self._prev  # restore (supports nesting)
        return False


def setInterval(sync_time: float) -> _AutoRefreshCtx:
    """Mark components in this block for periodic HTMX polling.

    Args:
        sync_time: Refresh cadence in seconds (minimum recommended: 1).

    Usage::

        with mt.setInterval(sync_time=10):
            mt.scatter_chart(data, id="live_chart")
    """
    return _AutoRefreshCtx(f"every {sync_time}s")


def setTimeout(delay: float) -> _AutoRefreshCtx:
    """Mark components in this block for a single delayed HTMX fetch.

    The component renders immediately with current data, then re-fetches
    once after *delay* seconds.

    Args:
        delay: Seconds to wait before the one-shot refresh.

    Usage::

        with mt.setTimeout(delay=5):
            mt.info("Checking status…", id="status_msg")
    """
    return _AutoRefreshCtx(f"load delay:{delay}s")
