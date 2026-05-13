# import pandas as pd  # Commented out for testing
from mxlit.context import get_context
from mxlit.layout import layout_manager

def _register_data_component(component_type: str, props: dict, id: str = None):
    """Helper to register data component."""
    ctx = get_context()
    if ctx:
        if ctx.mode == "init":
            component_id = layout_manager.register_component(
                component_type,
                props,
                component_id=id
            )
            return component_id
        else:
            ctx.add_component({"type": component_type, **props})
    return None

def dataframe(data):
    """Display a dataframe as an interactive table."""
    ctx = get_context()
    if ctx:
        # Simplified for testing without pandas
        html = f"<pre>{str(data)}</pre>"
        _register_data_component("dataframe", {"content": html})
    else:
        print(data)

def table(data):
    """Display a static table."""
    # For now, implemented same as dataframe
    ctx = get_context()
    if ctx:
        # Simplified for testing without pandas
        html = f"<pre>{str(data)}</pre>"
        _register_data_component("table", {"content": html})
    else:
        print(data)

def json(body):
    """Display object or string as a pretty-printed JSON string."""
    import json as json_lib
    ctx = get_context()
    if ctx:
        if isinstance(body, str):
            try:
                formatted = json_lib.dumps(json_lib.loads(body), indent=2)
            except:
                formatted = body
        else:
            formatted = json_lib.dumps(body, indent=2)
            
        ctx.add_component({"type": "json", "content": formatted})
    else:
        print(body)

def metric(label: str, value, delta=None, id: str = None):
    """Display a metric in big bold font, with an optional indicator of how the metric changed."""
    props = {
        "label": label,
        "value": str(value),
        "delta": str(delta) if delta is not None else None
    }
    component_id = _register_data_component("metric", props, id)
    if component_id:  # init mode
        return component_id
    if not get_context():
        print(f"{label}: {value} (Delta: {delta})")
