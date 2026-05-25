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

def line_chart(data, class_: str = "", **kwargs):
    """Display a line chart.

    Args:
        data: A list of values or a dict mapping labels to values.
        class_: Optional Tailwind utility classes applied to the chart wrapper.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart", "chart_type": "line",
            "data": _format_chart_data(data, "line"),
            "kwargs": kwargs, "key": _generate_key("line", data), "class_": class_
        })
    else:
        print("[Line Chart]")

def bar_chart(data, class_: str = "", **kwargs):
    """Display a bar chart.

    Args:
        data: A list of values or a dict mapping labels to values.
        class_: Optional Tailwind utility classes applied to the chart wrapper.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart", "chart_type": "bar",
            "data": _format_chart_data(data, "bar"),
            "kwargs": kwargs, "key": _generate_key("bar", data), "class_": class_
        })
    else:
        print("[Bar Chart]")

def area_chart(data, class_: str = "", **kwargs):
    """Display an area chart.

    Args:
        data: A list of values or a dict mapping labels to values.
        class_: Optional Tailwind utility classes applied to the chart wrapper.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart", "chart_type": "line",  # Chart.js line + fill=true
            "data": _format_chart_data(data, "area"),
            "kwargs": kwargs, "key": _generate_key("area", data), "class_": class_
        })
    else:
        print("[Area Chart]")

def scatter_chart(data, class_: str = "", **kwargs):
    """Display a scatter chart.

    Args:
        data: A dict with ``'x'`` and ``'y'`` lists, or a list of ``(x, y)`` pairs.
        class_: Optional Tailwind utility classes applied to the chart wrapper.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "chart", "chart_type": "scatter",
            "data": _format_chart_data(data, "scatter"),
            "kwargs": kwargs, "key": _generate_key("scatter", data), "class_": class_
        })
    else:
        print("[Scatter Chart]")
