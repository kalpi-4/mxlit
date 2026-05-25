import pandas as pd
from mxlit.context import get_context

def dataframe(data, class_: str = ""):
    """Display a dataframe as an interactive table.

    Args:
        data: A pandas DataFrame or any object convertible to one.
        class_: Optional Tailwind utility classes applied to the table wrapper.
    """
    ctx = get_context()
    if ctx:
        if isinstance(data, pd.DataFrame):
            html = data.to_html(classes="dataframe", border=0)
        else:
            try:
                html = pd.DataFrame(data).to_html(classes="dataframe", border=0)
            except Exception as e:
                html = f"<p>Error rendering dataframe: {e}</p>"
        ctx.add_component({"type": "dataframe", "content": html, "class_": class_})
    else:
        print(data)

def table(data, class_: str = ""):
    """Display a static table.

    Args:
        data: A pandas DataFrame or any object convertible to one.
        class_: Optional Tailwind utility classes applied to the table wrapper.
    """
    ctx = get_context()
    if ctx:
        if isinstance(data, pd.DataFrame):
            html = data.to_html(classes="table", border=0)
        else:
            try:
                html = pd.DataFrame(data).to_html(classes="table", border=0)
            except Exception as e:
                html = f"<p>Error rendering table: {e}</p>"
        ctx.add_component({"type": "table", "content": html, "class_": class_})
    else:
        print(data)

def json(body, class_: str = ""):
    """Display object or string as a pretty-printed JSON string.

    Args:
        body: A dict, list, or JSON string to display.
        class_: Optional Tailwind utility classes applied to the <pre> element.
    """
    import json as json_lib
    ctx = get_context()
    if ctx:
        if isinstance(body, str):
            try:
                formatted = json_lib.dumps(json_lib.loads(body), indent=2)
            except Exception:
                formatted = body
        else:
            formatted = json_lib.dumps(body, indent=2)
        ctx.add_component({"type": "json", "content": formatted, "class_": class_})
    else:
        print(body)

def metric(label: str, value, delta=None, class_: str = ""):
    """Display a metric with an optional delta indicator.

    Args:
        label: The metric label.
        value: The metric value.
        delta: Optional numeric change to show as an up/down indicator.
        class_: Optional Tailwind utility classes applied to the metric card.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "metric",
            "label": label,
            "value": str(value),
            "delta": str(delta) if delta is not None else None,
            "class_": class_
        })
    else:
        print(f"{label}: {value} (Delta: {delta})")
