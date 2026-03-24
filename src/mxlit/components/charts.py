from mxlit.context import get_context
import hashlib

def _generate_key(component_type: str, data) -> str:
    """Generate a unique key for a chart."""
    return hashlib.md5(f"{component_type}-{str(data)}".encode()).hexdigest()

def _format_chart_data(data, chart_type):
    if isinstance(data, list):
        labels = [str(i) for i in range(len(data))]
        datasets = [{"label": "Series", "data": data, "backgroundColor": "rgba(255, 75, 75, 0.5)", "borderColor": "#ff4b4b"}]
    elif isinstance(data, dict):
        if chart_type == "scatter" and "x" in data and "y" in data:
            labels = [str(x) for x in data["x"]]
            datasets = [{"label": "Series", "data": [{"x": x, "y": y} for x, y in zip(data["x"], data["y"])], "backgroundColor": "#ff4b4b"}]
        else:
            labels = list(data.keys())
            datasets = [{"label": "Series", "data": list(data.values()), "backgroundColor": "rgba(255, 75, 75, 0.5)", "borderColor": "#ff4b4b"}]
    else:
        labels = []
        datasets = []
        
    if chart_type == "area":
        for ds in datasets:
            ds["fill"] = True
            
    return {
        "labels": labels,
        "datasets": datasets
    }

def line_chart(data, **kwargs):
    """Display a line chart."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart",
            "chart_type": "line",
            "data": _format_chart_data(data, "line"),
            "kwargs": kwargs,
            "key": _generate_key("line", data)
        })
    else:
        print(f"[Line Chart]")

def bar_chart(data, **kwargs):
    """Display a bar chart."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart",
            "chart_type": "bar",
            "data": _format_chart_data(data, "bar"),
            "kwargs": kwargs,
            "key": _generate_key("bar", data)
        })
    else:
        print(f"[Bar Chart]")

def area_chart(data, **kwargs):
    """Display an area chart."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart",
            "chart_type": "line",  # Chart.js uses 'line' with fill=true for area charts
            "data": _format_chart_data(data, "area"),
            "kwargs": kwargs,
            "key": _generate_key("area", data)
        })
    else:
        print(f"[Area Chart]")

def scatter_chart(data, **kwargs):
    """Display a scatter chart."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart",
            "chart_type": "scatter",
            "data": _format_chart_data(data, "scatter"),
            "kwargs": kwargs,
            "key": _generate_key("scatter", data)
        })
    else:
        print(f"[Scatter Chart]")
