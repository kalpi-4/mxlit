from typing import Callable

from mxlit.components.base import BaseComponent, ComponentType, component


def _format_chart_data(data, chart_variant: str) -> dict:
    """Convert Python data to Chart.js dataset format."""
    if isinstance(data, list):
        labels   = [str(i) for i in range(len(data))]
        datasets = [{"label": "Series", "data": data,
                     "backgroundColor": "rgba(255, 75, 75, 0.5)",
                     "borderColor": "#ff4b4b"}]
    elif isinstance(data, dict):
        if chart_variant == "scatter" and "x" in data and "y" in data:
            labels   = [str(x) for x in data["x"]]
            datasets = [{"label": "Series",
                         "data": [{"x": x, "y": y} for x, y in zip(data["x"], data["y"])],
                         "backgroundColor": "#ff4b4b"}]
        else:
            labels   = list(data.keys())
            datasets = [{"label": "Series", "data": list(data.values()),
                         "backgroundColor": "rgba(255, 75, 75, 0.5)",
                         "borderColor": "#ff4b4b"}]
    else:
        labels, datasets = [], []

    if chart_variant in ("area", "area_chart"):
        for ds in datasets:
            ds["fill"] = True

    return {"labels": labels, "datasets": datasets}


def _make_chart(component_type: ComponentType, chart_js_type: str) -> Callable:
    """Generate a chart display function for the given chart type."""
    @component(component_type)
    def _fn(data, title: str = "", **kwargs) -> tuple[dict, Callable]:
        chart_key = BaseComponent.generate_key(component_type, str(data))
        return (
            {
                "chart_type": chart_js_type,
                "data":       _format_chart_data(data, component_type.value),
                "kwargs":     kwargs,
                "key":        chart_key,
                "title":      title,
            },
            lambda: print(f"[{component_type.value.replace('_', ' ').title()}]"),
        )

    _fn.__name__     = component_type.value
    _fn.__qualname__ = f"mxlit.components.charts.{component_type.value}"
    return _fn


line_chart    = _make_chart(ComponentType.LINE_CHART,    "line")
bar_chart     = _make_chart(ComponentType.BAR_CHART,     "bar")
area_chart    = _make_chart(ComponentType.AREA_CHART,    "line")  # area uses line + fill
scatter_chart = _make_chart(ComponentType.SCATTER_CHART, "scatter")
