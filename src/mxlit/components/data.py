import pandas as pd
from mxlit.context import get_context

def dataframe(data):
    """Display a dataframe as an interactive table."""
    ctx = get_context()
    if ctx:
        if isinstance(data, pd.DataFrame):
            html = data.to_html(classes="dataframe", border=0)
        else:
            try:
                html = pd.DataFrame(data).to_html(classes="dataframe", border=0)
            except Exception as e:
                html = f"<p>Error rendering dataframe: {e}</p>"
        
        ctx.add_component({"type": "dataframe", "content": html})
    else:
        print(data)

def table(data):
    """Display a static table."""
    # For now, implemented same as dataframe
    ctx = get_context()
    if ctx:
        if isinstance(data, pd.DataFrame):
            html = data.to_html(classes="table", border=0)
        else:
            try:
                html = pd.DataFrame(data).to_html(classes="table", border=0)
            except Exception as e:
                html = f"<p>Error rendering table: {e}</p>"
        
        ctx.add_component({"type": "table", "content": html})
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

def metric(label: str, value, delta=None):
    """Display a metric in big bold font, with an optional indicator of how the metric changed."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "metric", 
            "label": label, 
            "value": str(value), 
            "delta": str(delta) if delta is not None else None
        })
    else:
        print(f"{label}: {value} (Delta: {delta})")
