from __future__ import annotations

import functools
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Literal

# ── Render-order counter ───────────────────────────────────────────────────────
# Tracks per-type render index for auto-assigned display component ids.
# Must be reset before each script execution via reset_render_counts().
_RENDER_COUNTS: dict[str, int] = {}


def reset_render_counts() -> None:
    """Reset per-type render-order counters. Called before each script execution."""
    _RENDER_COUNTS.clear()


# ── HTMX type aliases ──────────────────────────────────────────────────────────

SwapStrategy = Literal[
    "innerHTML", "outerHTML", "textContent", "beforebegin", "afterbegin",
    "beforeend", "afterend", "delete", "none",
]
TriggerSpec   = str
ParamsSpec    = Literal["*", "none"] | str
EncodingType  = Literal["multipart/form-data", "application/x-www-form-urlencoded"]
HistorySpec   = Literal["false"]


# ── ComponentType Enum ─────────────────────────────────────────────────────────

class ComponentType(str, Enum):
    """Exhaustive typed registry of every mxlit component type identifier.

    Inheriting from str means ComponentType.TITLE == "title" is True,
    the value serialises to JSON unchanged, and Jinja2 comp.type == 'title'
    comparisons still hold — zero template changes required.
    """
    # Text
    WRITE          = "write"
    TITLE          = "title"
    HEADER         = "header"
    SUBHEADER      = "subheader"
    TEXT           = "text"
    MARKDOWN       = "markdown"
    CODE           = "code"
    HTML           = "html"
    LATEX          = "latex"
    BADGE          = "badge"
    NER            = "ner"
    WRITE_STREAM   = "write_stream"
    # Data
    DATAFRAME      = "dataframe"
    TABLE          = "table"
    JSON           = "json"
    METRIC         = "metric"
    # Widgets
    BUTTON         = "button"
    TEXT_INPUT     = "text_input"
    CHECKBOX       = "checkbox"
    SLIDER         = "slider"
    NUMBER_INPUT   = "number_input"
    TEXT_AREA      = "text_area"
    RADIO          = "radio"
    SELECTBOX      = "selectbox"
    TOGGLE         = "toggle"
    COLOR_PICKER   = "color_picker"
    DATE_INPUT     = "date_input"
    EMAIL_INPUT    = "email_input"
    PASSWORD_INPUT = "password_input"
    DATETIME_INPUT = "datetime_input"
    FILE_INPUT         = "file_input"
    MULTISELECT        = "multiselect"
    SELECT_SLIDER      = "select_slider"
    TIME_INPUT         = "time_input"
    LINK_BUTTON        = "link_button"
    DOWNLOAD_BUTTON    = "download_button"
    PILLS              = "pills"
    FEEDBACK           = "feedback"
    # Layout — composite containers
    CONTAINER      = "container"
    SIDEBAR        = "sidebar"
    COLUMN         = "column"   # individual slot produced by columns()
    COLUMNS        = "columns"  # kept for backward-compat (not used internally)
    TAB            = "tab"      # individual panel produced by tabs()
    TABS           = "tabs"     # kept for backward-compat (not used internally)
    EXPANDER       = "expander"
    CARD           = "card"
    # Media
    IMAGE          = "image"
    AUDIO          = "audio"
    VIDEO          = "video"
    LOGO           = "logo"
    # Charts
    LINE_CHART     = "line_chart"
    BAR_CHART      = "bar_chart"
    AREA_CHART     = "area_chart"
    SCATTER_CHART  = "scatter_chart"
    # Status
    STATUS         = "status"
    # OAT UI primitives
    SPINNER        = "spinner"
    SKELETON       = "skeleton"
    PROGRESS       = "progress"
    METER          = "meter"
    AVATAR         = "avatar"
    AVATAR_GROUP   = "avatar_group"
    DIALOG         = "dialog"
    DROPDOWN       = "dropdown"
    BREADCRUMB     = "breadcrumb"
    BUTTON_GROUP   = "button_group"
    GRID           = "grid"
    # Spacer / placeholder
    SPACE          = "space"
    EMPTY          = "empty"
    # Popover / status
    POPOVER        = "popover"
    STATUS_BOX     = "status_box"
    # Notifications / navigation / grouping
    TOAST          = "toast"
    PAGINATION     = "pagination"
    INPUT_GROUP    = "input_group"


# ── HtmxProps ─────────────────────────────────────────────────────────────────

@dataclass
class HtmxProps:
    """Strongly-typed container for every HTMX attribute.

    Every field maps 1-to-1 to an hx-* HTML attribute.
    Fields left at None/False are excluded from to_attrs() so component
    dicts stay minimal.
    """

    # HTTP method
    post:   str | None = "/interact"
    get:    str | None = None
    put:    str | None = None
    patch:  str | None = None
    delete: str | None = None

    # Targeting & swapping
    target:     str | None = "#app-root"
    swap:       str | None = "innerHTML settle:0"
    swap_oob:   str | None = None
    select:     str | None = None
    select_oob: str | None = None

    # Triggering
    trigger:  TriggerSpec | None = "change"
    boost:    bool               = False
    validate: bool               = False

    # Request customisation
    vals:         dict[str, Any] | str | None = None
    headers:      dict[str, str] | str | None = None
    include:      str | None                  = None
    params:       ParamsSpec | None           = None
    encoding:     EncodingType | None         = None
    request:      dict[str, Any] | str | None = None
    sync:         str | None                  = None
    disabled_elt: str | None                  = None
    indicator:    str | None                  = None
    confirm:      str | None                  = None
    prompt:       str | None                  = None
    ext:          str | None                  = None

    # History & URL
    push_url:    str | bool | None = None
    replace_url: str | bool | None = None
    history:     HistorySpec | None = None
    history_elt: bool               = False

    # Inheritance control
    disable:    bool       = False
    disinherit: str | None = None
    inherit:    str | None = None
    preserve:   bool       = False

    @staticmethod
    def _json_or_str(value: dict | str) -> str:
        return json.dumps(value, separators=(",", ":")) if isinstance(value, dict) else value

    @staticmethod
    def _bool_url(value: str | bool) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return value

    def to_attrs(self) -> dict[str, str]:
        """Serialise to a flat hx-* dict merged by BaseComponent.to_dict()."""
        d: dict[str, str] = {}
        if self.post    is not None: d["hx-post"]   = self.post
        if self.get     is not None: d["hx-get"]    = self.get
        if self.put     is not None: d["hx-put"]    = self.put
        if self.patch   is not None: d["hx-patch"]  = self.patch
        if self.delete  is not None: d["hx-delete"] = self.delete
        if self.target     is not None: d["hx-target"]     = self.target
        if self.swap       is not None: d["hx-swap"]       = self.swap
        if self.swap_oob   is not None: d["hx-swap-oob"]   = self.swap_oob
        if self.select     is not None: d["hx-select"]     = self.select
        if self.select_oob is not None: d["hx-select-oob"] = self.select_oob
        if self.trigger  is not None: d["hx-trigger"]  = self.trigger
        if self.boost:                d["hx-boost"]    = ""
        if self.validate:             d["hx-validate"] = ""
        if self.vals         is not None: d["hx-vals"]         = self._json_or_str(self.vals)
        if self.headers      is not None: d["hx-headers"]      = self._json_or_str(self.headers)
        if self.include      is not None: d["hx-include"]      = self.include
        if self.params       is not None: d["hx-params"]       = self.params
        if self.encoding     is not None: d["hx-encoding"]     = self.encoding
        if self.request      is not None: d["hx-request"]      = self._json_or_str(self.request)
        if self.sync         is not None: d["hx-sync"]         = self.sync
        if self.disabled_elt is not None: d["hx-disabled-elt"] = self.disabled_elt
        if self.indicator    is not None: d["hx-indicator"]    = self.indicator
        if self.confirm      is not None: d["hx-confirm"]      = self.confirm
        if self.prompt       is not None: d["hx-prompt"]       = self.prompt
        if self.ext          is not None: d["hx-ext"]          = self.ext
        if self.push_url    is not None: d["hx-push-url"]    = self._bool_url(self.push_url)
        if self.replace_url is not None: d["hx-replace-url"] = self._bool_url(self.replace_url)
        if self.history     is not None: d["hx-history"]     = self.history
        if self.history_elt:             d["hx-history-elt"] = ""
        if self.disable:                d["hx-disable"]    = ""
        if self.disinherit is not None: d["hx-disinherit"] = self.disinherit
        if self.inherit    is not None: d["hx-inherit"]    = self.inherit
        if self.preserve:               d["hx-preserve"]   = ""
        return d


# ── OatProps ──────────────────────────────────────────────────────────────────

@dataclass
class OatProps:
    """Typed carrier for OAT semantic HTML attributes."""
    variant: str | None        = None
    role:    str | None        = None
    field:   str | bool | None = None
    busy:    bool              = False
    spinner: str | None        = None
    tooltip: str | None        = None

    def to_attrs(self) -> dict[str, str]:
        d: dict[str, str] = {}
        if self.variant:
            d["data-variant"] = self.variant
        if self.role:
            d["role"] = self.role
        if self.field is not None:
            d["data-field"] = "" if self.field is True else str(self.field)
        if self.busy:
            d["aria-busy"] = "true"
        if self.spinner:
            d["data-spinner"] = self.spinner
        if self.tooltip:
            d["title"] = self.tooltip
        return d


# ── BaseComponent ─────────────────────────────────────────────────────────────

@dataclass
class BaseComponent:
    """Root of the mxlit component hierarchy.

    Lifecycle:
    1. Component function constructs a BaseComponent instance.
    2. __post_init__ calls _register().
    3. _register() appends to the active AppContext or calls _fallback_fn.
    """
    type:         ComponentType
    id:           str               = ""
    className:    str               = ""
    props:        dict[str, Any]    = field(default_factory=dict)
    _htmx:        HtmxProps | None = field(default=None, repr=False)
    _oat:         OatProps  | None = field(default=None, repr=False)
    _fallback_fn: Callable  | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self._register()

    def _register(self) -> None:
        from mxlit.context import get_context  # local import avoids circular
        ctx = get_context()
        if ctx:
            ctx.add_component(self.to_dict())
        elif self._fallback_fn is not None:
            self._fallback_fn()

    def to_dict(self) -> dict[str, Any]:
        """Produce the flat dict consumed by the Jinja2 render_component macro.

        id resolution order:
        1. self.id — non-empty string supplied by the caller
        2. props["key"] — present for all widgets (MD5 hash)
        3. "" — display components without a key (auto-assigned by @component decorator)
        """
        resolved_id = self.id or self.props.get("key", "")
        type_val = self.type.value if isinstance(self.type, ComponentType) else str(self.type)
        d: dict[str, Any] = {"type": type_val, "id": resolved_id, "class_": self.className}
        d.update(self.props)
        if self._htmx is not None:
            d.update(self._htmx.to_attrs())
        if self._oat is not None:
            d.update(self._oat.to_attrs())
        return d

    @staticmethod
    def generate_key(component_type: ComponentType | str, discriminator: str) -> str:
        """Stable MD5-based widget key — single canonical implementation."""
        type_str = (
            component_type.value
            if isinstance(component_type, ComponentType)
            else str(component_type)
        )
        return hashlib.md5(f"{type_str}-{discriminator}".encode()).hexdigest()


# ── CompositeComponent ────────────────────────────────────────────────────────

@dataclass
class CompositeComponent(BaseComponent):
    """A BaseComponent that nests children via a `with` block.

    Registration is deferred to __exit__ so all children are collected first.
    """
    _children:     list          = field(default_factory=list, repr=False, init=False)
    _saved_target: list | None   = field(default=None,         repr=False, init=False)
    _active_ctx:   object | None = field(default=None,         repr=False, init=False)

    def __post_init__(self) -> None:
        pass  # Skip immediate registration; defer to __exit__

    def __enter__(self) -> "CompositeComponent":
        from mxlit.context import get_context
        ctx = get_context()
        if ctx:
            self._active_ctx   = ctx
            self._saved_target = ctx.current_target
            ctx.current_target = self._children
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._active_ctx:
            self._active_ctx.current_target = self._saved_target
            self._active_ctx = None
        self._register()
        return False

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["children"] = list(self._children)
        return d


# ── Factory decorators ────────────────────────────────────────────────────────

def component(
    component_type: ComponentType,
    *,
    htmx: HtmxProps | None = None,
    oat:  OatProps  | None = None,
) -> Callable:
    """Decorator turning a props-builder into a registered display component.

    The wrapped function must return (props: dict, fallback_fn: Callable | None).
    The decorator pops 'id', 'className', and 'class_' (compat alias) from kwargs.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> None:
            custom_id = kwargs.pop("id", "")
            className = kwargs.pop("className", kwargs.pop("class_", ""))
            props, fallback_fn = fn(*args, **kwargs)
            if custom_id:
                resolved_id = custom_id
            else:
                idx = _RENDER_COUNTS.get(component_type, 0)
                _RENDER_COUNTS[component_type] = idx + 1
                resolved_id = f"{component_type.value}-{idx}"
            BaseComponent(
                type         = component_type,
                id           = resolved_id,
                className    = className,
                props        = props,
                _htmx        = htmx,
                _oat         = oat,
                _fallback_fn = fallback_fn,
            )
        return wrapper
    return decorator


def widget_component(
    component_type: ComponentType,
    *,
    htmx: HtmxProps | None = None,
    oat:  OatProps  | None = None,
) -> Callable:
    """Decorator registering a stateful widget and preserving its return value.

    The wrapped function must return (props: dict, return_value: Any).
    Session-state reads happen inside the wrapped function.
    The decorator pops 'id', 'className', and 'class_' (compat alias) from kwargs.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            custom_id = kwargs.pop("id", "")
            className = kwargs.pop("className", kwargs.pop("class_", ""))
            props, return_value = fn(*args, **kwargs)
            BaseComponent(
                type      = component_type,
                id        = custom_id,
                className = className,
                props     = props,
                _htmx     = htmx,
                _oat      = oat,
            )
            return return_value
        return wrapper
    return decorator
