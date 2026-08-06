from typing import Callable

from mxlit.components.base import (
    BaseComponent, ComponentType, OatProps, component,
)


def _make_status_variant(status_type: str) -> Callable:
    """Generate a status display function for the given OAT variant."""
    preset_oat = OatProps(variant=status_type, role="alert")

    @component(ComponentType.STATUS, oat=preset_oat)
    def _fn(body: str) -> tuple[dict, Callable]:
        return (
            {"content": body, "status_type": status_type},
            lambda: print(f"[{status_type.upper()}] {body}"),
        )

    _fn.__name__     = status_type
    _fn.__qualname__ = f"mxlit.components.status.{status_type}"
    return _fn


error   = _make_status_variant("error")
warning = _make_status_variant("warning")
success = _make_status_variant("success")
info    = _make_status_variant("info")


def exception(e: Exception, **kwargs):
    """Display an exception as an error alert."""
    body = f"{type(e).__name__}: {str(e)}"
    BaseComponent(
        type         = ComponentType.STATUS,
        className    = kwargs.pop("class_", kwargs.pop("className", "")),
        props        = {"content": body, "status_type": "error"},
        _oat         = OatProps(variant="error", role="alert"),
        _fallback_fn = lambda: print(f"[EXCEPTION] {body}"),
    )
