import pandas as pd
from typing import Callable

from mxlit.components.base import ComponentType, component


@component(ComponentType.DATAFRAME)
def dataframe(data) -> tuple[dict, Callable]:
    """Display a dataframe as a styled HTML table."""
    if isinstance(data, pd.DataFrame):
        html = data.to_html(classes="dataframe", border=0)
    else:
        try:
            html = pd.DataFrame(data).to_html(classes="dataframe", border=0)
        except Exception as e:
            html = f"<p>Error rendering dataframe: {e}</p>"
    return ({"content": html}, lambda: print(data))


@component(ComponentType.TABLE)
def table(data) -> tuple[dict, Callable]:
    """Display a static table."""
    if isinstance(data, pd.DataFrame):
        html = data.to_html(classes="table", border=0)
    else:
        try:
            html = pd.DataFrame(data).to_html(classes="table", border=0)
        except Exception as e:
            html = f"<p>Error rendering table: {e}</p>"
    return ({"content": html}, lambda: print(data))


@component(ComponentType.JSON)
def json(body) -> tuple[dict, Callable]:
    """Display an object or string as pretty-printed JSON."""
    import json as json_lib
    if isinstance(body, str):
        try:
            formatted = json_lib.dumps(json_lib.loads(body), indent=2)
        except Exception:
            formatted = body
    else:
        formatted = json_lib.dumps(body, indent=2)
    return ({"content": formatted}, lambda: print(body))


@component(ComponentType.METRIC)
def metric(label: str, value, delta=None) -> tuple[dict, Callable]:
    """Display a metric with an optional delta indicator."""
    props = {
        "label": label,
        "value": str(value),
        "delta": str(delta) if delta is not None else None,
    }
    return (props, lambda: print(f"{label}: {value} (Delta: {delta})"))
