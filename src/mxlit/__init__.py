import sys
import functools

from mxlit._exceptions import RerunException
from mxlit.context import get_context
from mxlit.state import session_state

# Text
from mxlit.components.text import (
    write, title, header, subheader, text, markdown, code, html,
    write_stream, ner_text, latex, badge,
)
# Data
from mxlit.components.data import dataframe, table, json, metric
# Widgets
from mxlit.components.widgets import (
    button, text_input, checkbox, slider, number_input, text_area,
    radio, selectbox, toggle, color_picker, date_input,
    email_input, password_input, datetime_input,
    file_input, pagination,
    multiselect, select_slider, time_input,
    link_button, download_button, pills, feedback,
)
# Layout
from mxlit.components.layout import (
    navbar, sidebar, columns, tabs, expander, container, page_config,
    card, spinner, progress, skeleton, meter,
    avatar, avatar_group, breadcrumb, button_group, toast,
    dialog, dropdown, grid, input_group,
    space, empty, popover, status,
)
# Media
from mxlit.components.media import image, audio, video, logo
# Charts
from mxlit.components.charts import line_chart, bar_chart, area_chart, scatter_chart
# Status components
from mxlit.components.status import error, warning, info, success, exception
# Theme
from mxlit.components.theme import theme
# Auto-refresh
from mxlit.timers import setInterval, setTimeout


def stop():
    """Stop execution immediately."""
    sys.exit(0)


def rerun():
    """Rerun script immediately."""
    raise RerunException("Rerun triggered")


# ── Caching ───────────────────────────────────────────────────────────────────

def cache_data(func=None, *, max_entries: int = 128, ttl: int = None, **_kwargs):
    """Cache the return value of a data-producing function across re-runs.

    Wraps the decorated function with ``functools.lru_cache`` so repeated calls
    with identical arguments return the cached result without re-executing.

    Usage::

        @mt.cache_data
        def load_df(path: str) -> pd.DataFrame:
            return pd.read_csv(path)

    Args:
        max_entries: Maximum number of cached results (default 128).
        ttl:         Ignored (included for Streamlit API compatibility).
    """
    decorator = functools.lru_cache(maxsize=max_entries)
    if func is None:
        return decorator
    return decorator(func)


def cache_resource(func=None, *, max_entries: int = 128, **_kwargs):
    """Cache a global resource (DB connection, ML model, etc.) across re-runs.

    Identical to :func:`cache_data` in the current implementation — both
    use ``functools.lru_cache``.  The distinction is semantic: use
    ``cache_resource`` for shared singleton objects, ``cache_data`` for
    pure-data results.

    Usage::

        @mt.cache_resource
        def load_model():
            return torch.load("model.pt")
    """
    decorator = functools.lru_cache(maxsize=max_entries)
    if func is None:
        return decorator
    return decorator(func)


# ── App options ───────────────────────────────────────────────────────────────

_OPTIONS: dict = {
    "client.showErrorDetails": True,
    "client.toolbarMode": "auto",
    "server.maxUploadSize": 200,
}


def get_option(key: str):
    """Return the current value of a mxlit option.

    Args:
        key: Option name (e.g. ``'client.showErrorDetails'``).

    Raises:
        KeyError: If the key is not a known option.
    """
    if key not in _OPTIONS:
        raise KeyError(f"Unknown option '{key}'. Available: {list(_OPTIONS)}")
    return _OPTIONS[key]


def set_option(key: str, value) -> None:
    """Set a mxlit option value.

    Args:
        key:   Option name.
        value: New value.
    """
    _OPTIONS[key] = value
