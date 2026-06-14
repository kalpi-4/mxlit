from mxlit.context import get_context
from mxlit.components.base import (
    BaseComponent, ComponentType, CompositeComponent, OatProps, component, HtmxProps,
    widget_component,
)
from mxlit.state import session_state


# ── Layout containers — all backed by CompositeComponent ─────────────────────

class Sidebar:
    """Singleton context manager for the sidebar layout region.

    Can be used in two ways::

        # As a bare context manager (uses default class)
        with mt.sidebar:
            mt.title("Nav")

        # As a callable returning a configured context manager
        with mt.sidebar(className="w-64"):
            mt.title("Nav")

    Internally each ``with`` block creates a fresh :class:`CompositeComponent`
    so there is no cross-request state leak on the singleton object.
    """

    def __call__(self, className: str = "") -> CompositeComponent:
        return CompositeComponent(
            type=ComponentType.SIDEBAR,
            className=className,
            props={},
        )

    def __enter__(self) -> CompositeComponent:
        self._cm = self()
        return self._cm.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return self._cm.__exit__(exc_type, exc_val, exc_tb)


sidebar = Sidebar()


def columns(spec, vertical_alignment: str = "top", className: str = "") -> list[CompositeComponent]:
    """Create a set of columns backed by :class:`CompositeComponent`.

    Each returned element is a context manager that collects its children
    and registers itself as a ``'column'`` component.

    Args:
        spec: Number of equal columns (int) or list of relative weights.
        vertical_alignment: ``'top'`` (default), ``'center'``, or ``'bottom'``.
        className: Tailwind classes applied to the outer columns wrapper ``<div>``.

    Example::

        col1, col2 = mt.columns(2)
        with col1:
            mt.metric("Revenue", "$42k")
        with col2:
            mt.metric("Cost", "$18k")
    """
    weights = [1] * spec if isinstance(spec, int) else list(spec)
    return [
        CompositeComponent(
            type=ComponentType.COLUMN,
            props={
                "weight": w,
                "columnsClassName": className,
                "vertical_alignment": vertical_alignment,
            },
        )
        for w in weights
    ]


def tabs(tabs_spec: list[str], className: str = "") -> list[CompositeComponent]:
    """Create a set of tab panels backed by :class:`CompositeComponent`.

    Each returned element is a context manager that collects its children
    and registers itself as a ``'tab'`` component.

    Args:
        tabs_spec: List of tab label strings.
        className: Tailwind classes applied to the outer ``<ot-tabs>`` element.

    Example::

        tab_a, tab_b = mt.tabs(["Summary", "Detail"])
        with tab_a:
            mt.write("Summary content")
        with tab_b:
            mt.write("Detail content")
    """
    return [
        CompositeComponent(
            type=ComponentType.TAB,
            props={"label": label, "tabsClassName": className},
        )
        for label in tabs_spec
    ]


def expander(label: str, icon: str = None, className: str = "") -> CompositeComponent:
    """Create an expandable ``<details>`` container.

    Args:
        label:     Text shown in the ``<summary>`` element.
        icon:      Optional emoji or icon prepended to the label.
        className: Extra CSS classes on the ``<details>`` element.
    """
    return CompositeComponent(
        type=ComponentType.EXPANDER,
        className=className,
        props={"label": label, "icon": icon},
    )


def container(horizontal: bool = False, className: str = "") -> CompositeComponent:
    """Create a general-purpose layout container.

    Args:
        horizontal: If ``True``, renders children in a horizontal ``hstack`` row.
        className:  Extra CSS classes on the wrapping ``<div>``.
    """
    return CompositeComponent(
        type=ComponentType.CONTAINER,
        className=className,
        props={"horizontal": horizontal},
    )


def page_config(main_class: str = "", aside_class: str = ""):
    """Set extra Tailwind classes on the top-level layout elements."""
    ctx = get_context()
    if ctx:
        ctx.main_class  = main_class
        ctx.aside_class = aside_class


# ── navbar — CompositeComponent ───────────────────────────────────────────────

def navbar(**kwargs) -> CompositeComponent:
    """Full-width top navbar rendered above the sidebar layout.

    Usage::

        with mt.navbar():
            mt.write("My App")
    """
    className = kwargs.pop("className", "")
    custom_id = kwargs.pop("id", "")
    return CompositeComponent(
        type      = ComponentType.NAVBAR,
        id        = custom_id,
        className = className,
        props     = {},
    )


# ── card — CompositeComponent via BaseComponent ───────────────────────────────

def card(header: str = "", footer: str = "", **kwargs) -> CompositeComponent:
    """Create a card container using OAT's <article class="card"> pattern.

    Usage::

        with mt.card("Sales Summary"):
            mt.metric("Revenue", "$42k", delta="+8%")
    """
    className = kwargs.pop("className", "")
    custom_id = kwargs.pop("id", "")
    return CompositeComponent(
        type      = ComponentType.CARD,
        id        = custom_id,
        className = className,
        props     = {"header": header, "footer": footer},
    )


# ── Leaf OAT UI primitives ────────────────────────────────────────────────────

@component(ComponentType.SPINNER, oat=OatProps(busy=True))
def spinner(size: str = "large") -> tuple[dict, None]:
    """Display a loading spinner.

    Args:
        size: 'small', 'large' (default), or 'overlay'.
    """
    return ({"size": size}, None)


@component(ComponentType.PROGRESS)
def progress(value: float = None, max: float = 1.0) -> tuple[dict, None]:
    """Display a progress bar.

    Args:
        value: Current progress (0.0–max). Omit for indeterminate.
        max:   Maximum value (default 1.0).
    """
    return ({"value": value, "max": max}, None)


@component(ComponentType.SKELETON)
def skeleton(variant: str = "line") -> tuple[dict, None]:
    """Display a skeleton loading placeholder.

    Args:
        variant: 'line' (default) or 'box'.
    """
    return ({"variant": variant}, None)


@component(ComponentType.METER)
def meter(value: float, min: float = 0.0, max: float = 1.0,
          low: float = None, high: float = None,
          optimum: float = None) -> tuple[dict, None]:
    """Display a native <meter> element with semantic color cues.

    Args:
        value:   Current value.
        min:     Minimum value (default 0.0).
        max:     Maximum value (default 1.0).
        low:     Value below which the bar turns yellow.
        high:    Value above which the bar turns yellow.
        optimum: Optimal value for color cue reference.
    """
    return (
        {"value": value, "min": min, "max": max,
         "low": low, "high": high, "optimum": optimum},
        None,
    )


# ── Avatar ────────────────────────────────────────────────────────────────────

@component(ComponentType.AVATAR)
def avatar(src: str = "", initials: str = "", size: str = "") -> tuple[dict, None]:
    """Display an avatar image or initials badge using OAT's <figure data-variant="avatar">.

    Args:
        src:      URL of the avatar image. If empty, ``initials`` text is shown instead.
        initials: 1–2 character label; shown as fallback text and as ``aria-label``.
        size:     ``'small'`` or ``'large'`` (default is browser/OAT default size).
    """
    return ({"src": src, "initials": initials, "size": size}, None)


@component(ComponentType.AVATAR_GROUP)
def avatar_group(avatars: list, size: str = "") -> tuple[dict, None]:
    """Group multiple avatars together in OAT's stacked avatar pattern.

    Args:
        avatars: List of dicts with optional keys ``src``, ``initials``, ``size``.
                 Example: ``[{"initials": "JD"}, {"src": "/img/avatar.png"}]``
        size:    ``'small'`` or ``'large'`` — applied to the group wrapper.
    """
    return ({"avatars": avatars, "size": size}, None)


# ── Breadcrumb ────────────────────────────────────────────────────────────────

@component(ComponentType.BREADCRUMB)
def breadcrumb(items: list) -> tuple[dict, None]:
    """Display a breadcrumb navigation trail.

    Args:
        items: List of dicts with a required ``'label'`` key and optional ``'href'``.
               The **last** item is automatically marked ``aria-current="page"`` and
               is not rendered as a link.

    Example::

        mt.breadcrumb([
            {"label": "Home", "href": "/"},
            {"label": "Products", "href": "/products"},
            {"label": "Detail"},
        ])
    """
    return ({"items": items}, None)


# ── Button Group ──────────────────────────────────────────────────────────────

@component(ComponentType.BUTTON_GROUP)
def button_group(labels: list, key_prefix: str = "") -> tuple[dict, None]:
    """Render a connected segmented group of buttons using OAT's <menu class="buttons">.

    Each button posts to ``/interact`` and triggers a full page re-render.
    Read individual button state with ``mt.session_state.get(key)``.

    Args:
        labels:     List of button label strings.
        key_prefix: Optional prefix prepended to each button's auto-generated key.
    """
    buttons = [
        {"label": lbl, "key": BaseComponent.generate_key(ComponentType.BUTTON, f"{key_prefix}{lbl}")}
        for lbl in labels
    ]
    return ({"buttons": buttons}, None)


# ── Toast ─────────────────────────────────────────────────────────────────────

@component(ComponentType.TOAST)
def toast(message: str, title: str = "", variant: str = "",
          placement: str = "top-right", duration: int = 4000) -> tuple[dict, None]:
    """Show a toast notification via ``ot.toast()`` JS call.

    This component emits a hidden ``<script>`` that calls the oat.ink
    ``ot.toast()`` function. No visible DOM element is added.

    Args:
        message:   Body text of the toast.
        title:     Optional heading displayed above the body.
        variant:   ``'success'``, ``'danger'``, or ``'warning'``.
        placement: ``'top-right'`` (default), ``'top-left'``,
                   ``'bottom-right'``, or ``'bottom-left'``.
        duration:  Milliseconds before auto-dismissal (default 4000).
    """
    return (
        {"message": message, "title": title, "variant": variant,
         "placement": placement, "duration": duration},
        None,
    )


# ── Dialog ────────────────────────────────────────────────────────────────────

def dialog(title: str = "", trigger_label: str = "Open", **kwargs) -> CompositeComponent:
    """Create a modal dialog using OAT's ``<dialog closedby="any">`` pattern.

    A trigger button is rendered immediately before the ``<dialog>`` element.
    Content placed inside the ``with`` block becomes the dialog body.

    Usage::

        with mt.dialog("Confirm", trigger_label="Delete"):
            mt.write("Are you sure you want to delete this item?")
            mt.button("Yes, delete")
    """
    custom_id = kwargs.pop("id", "")
    className = kwargs.pop("className", "")
    return CompositeComponent(
        type      = ComponentType.DIALOG,
        id        = custom_id,
        className = className,
        props     = {"title": title, "trigger_label": trigger_label},
    )


# ── Dropdown ──────────────────────────────────────────────────────────────────

@component(ComponentType.DROPDOWN)
def dropdown(label: str, items: list = None) -> tuple[dict, None]:
    """Render an ``<ot-dropdown>`` WebComponent menu.

    Args:
        label: Text shown on the trigger button.
        items: List of dicts with a required ``'label'`` key and optional ``'href'``.
               Items without ``href`` are rendered as plain ``<button>`` elements.

    Example::

        mt.dropdown("Options", items=[
            {"label": "Edit",   "href": "/edit"},
            {"label": "Delete"},
        ])
    """
    return ({"label": label, "items": items or []}, None)


# ── Grid ──────────────────────────────────────────────────────────────────────

def grid(**kwargs) -> CompositeComponent:
    """Wrap children in OAT's 12-column grid container (``<div class="container">``).

    Children receive a ``<div class="mx-component">`` wrapper; use ``className`` on
    each child to apply column-span classes (``col-6``, ``col-4``, etc.).

    Usage::

        with mt.grid():
            mt.write("Full-width content")
    """
    custom_id = kwargs.pop("id", "")
    className = kwargs.pop("className", "")
    return CompositeComponent(
        type      = ComponentType.GRID,
        id        = custom_id,
        className = className,
        props     = {},
    )


# ── Input Group ───────────────────────────────────────────────────────────────

def input_group(prefix: str = "", suffix: str = "", **kwargs) -> CompositeComponent:
    """Combine an input with a prefix label or suffix action using ``<fieldset class="group">``.

    Usage::

        with mt.input_group(prefix="https://", suffix=".com"):
            mt.text_input("Domain")
    """
    custom_id = kwargs.pop("id", "")
    className = kwargs.pop("className", "")
    return CompositeComponent(
        type      = ComponentType.INPUT_GROUP,
        id        = custom_id,
        className = className,
        props     = {"prefix": prefix, "suffix": suffix},
    )


# ── Space / Empty ─────────────────────────────────────────────────────────────

@component(ComponentType.SPACE)
def space(n: float = 1.0) -> tuple[dict, None]:
    """Insert vertical whitespace.

    Args:
        n: Multiplier in ``rem`` units (default ``1.0`` ≈ one line-height).
    """
    return ({"n": n}, None)


@component(ComponentType.EMPTY)
def empty() -> tuple[dict, None]:
    """Insert an empty placeholder div.

    Useful as a structural separator or a future swap target.
    """
    return ({}, None)


# ── Popover ───────────────────────────────────────────────────────────────────

def popover(label: str, **kwargs) -> CompositeComponent:
    """Create a popover panel triggered by a button (HTML Popover API).

    Usage::

        with mt.popover("Settings ⚙"):
            mt.toggle("Dark mode", key="dark_mode")

    The trigger button and the popover ``<div popover>`` are emitted together.
    Popover content is rendered inside the popover panel.

    Args:
        label:     Text shown on the trigger button.
        className: Extra CSS classes on the trigger button.
    """
    custom_id = kwargs.pop("id", "")
    className = kwargs.pop("className", "")
    return CompositeComponent(
        type      = ComponentType.POPOVER,
        id        = custom_id,
        className = className,
        props     = {"label": label},
    )


# ── Status container ──────────────────────────────────────────────────────────

def status(label: str, state: str = "running", **kwargs) -> CompositeComponent:
    """Create an expandable status container with a state indicator.

    Renders as an OAT ``<details>`` with a spinner, check-mark, or error icon
    depending on ``state``.

    Args:
        label:  Text shown in the summary row.
        state:  ``'running'`` (spinner), ``'complete'`` (✓), or ``'error'`` (✗).
        class_: Extra CSS classes.

    Usage::

        with mt.status("Fetching data…", state="running"):
            mt.write("Connecting to API…")
    """
    custom_id = kwargs.pop("id", "")
    className = kwargs.pop("className", "")
    return CompositeComponent(
        type      = ComponentType.STATUS_BOX,
        id        = custom_id,
        className = className,
        props     = {"label": label, "state": state},
    )
