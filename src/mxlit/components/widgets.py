import base64
import json as _json

from mxlit.components.base import (
    BaseComponent, ComponentType, HtmxProps, OatProps, component, widget_component,
)
from mxlit.state import session_state

# Shared HtmxProps instances (one per widget type, not one per call)
_HTMX_CHANGE     = HtmxProps(trigger="change")
_HTMX_CLICK      = HtmxProps(trigger="click, change")
_HTMX_SLIDER     = HtmxProps(trigger="change, input delay:500ms")
_OAT_FIELD       = OatProps(field=True)


@widget_component(ComponentType.BUTTON, htmx=HtmxProps(trigger="click"))
def button(label: str, key: str = None, disabled: bool = False,
           variant: str = None) -> tuple[dict, bool]:
    """Display a button widget. Returns True if clicked on this run.

    Args:
        variant: OAT semantic variant — ``None`` (default) is OAT's primary
                 filled style, or ``'secondary'`` / ``'danger'``. Style
                 modifiers (``'outline'``, ``'ghost'``, ``'small'``, ``'large'``)
                 are plain classes — pass them via ``className=``.
    """
    widget_key = key or BaseComponent.generate_key(ComponentType.BUTTON, label)
    clicked = session_state.get(widget_key, "false") == "true"
    if widget_key in session_state:
        session_state[widget_key] = "false"
    return ({"label": label, "key": widget_key, "disabled": disabled,
              "variant": variant}, clicked)


@widget_component(ComponentType.TEXT_INPUT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def text_input(label: str, value: str = "", key: str = None,
               disabled: bool = False) -> tuple[dict, str]:
    """Display a single-line text input. Returns current value."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.TEXT_INPUT, label)
    current_value = session_state.get(widget_key, value)
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@widget_component(ComponentType.CHECKBOX, htmx=_HTMX_CLICK, oat=_OAT_FIELD)
def checkbox(label: str, value: bool = False, key: str = None,
             disabled: bool = False) -> tuple[dict, bool]:
    """Display a checkbox widget. Returns current checked state."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.CHECKBOX, label)
    state_val     = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@widget_component(ComponentType.SLIDER, htmx=_HTMX_SLIDER, oat=_OAT_FIELD)
def slider(label: str, min_value: int = 0, max_value: int = 100,
           value: int = None, key: str = None,
           disabled: bool = False) -> tuple[dict, int]:
    """Display a slider widget. Returns current integer value."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.SLIDER, label)
    default_val   = value if value is not None else min_value
    current_value = int(session_state.get(widget_key, default_val))
    return (
        {"label": label, "min_value": min_value, "max_value": max_value,
         "value": current_value, "key": widget_key, "disabled": disabled},
        current_value,
    )


@widget_component(ComponentType.NUMBER_INPUT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def number_input(label: str, min_value=None, max_value=None, value=0,
                 key: str = None, disabled: bool = False, **kwargs):
    """Display a number input widget. Returns current numeric value."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.NUMBER_INPUT, label)
    is_float      = any(isinstance(v, float) for v in (min_value, max_value, value) if v is not None)
    type_cast     = float if is_float else int
    current_value = type_cast(session_state.get(widget_key, value))
    return (
        {"label": label, "min_value": min_value, "max_value": max_value,
         "value": current_value, "step": kwargs.get("step"), "key": widget_key,
         "disabled": disabled},
        current_value,
    )


@widget_component(ComponentType.TEXT_AREA, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def text_area(label: str, value: str = "", key: str = None,
              disabled: bool = False) -> tuple[dict, str]:
    """Display a multi-line text input. Returns current value."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.TEXT_AREA, label)
    current_value = session_state.get(widget_key, value)
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@widget_component(ComponentType.RADIO, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def radio(label: str, options: list, index: int = 0, key: str = None,
          disabled: bool = False) -> tuple[dict, str]:
    """Display a radio button group. Returns the selected option string."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.RADIO, label)
    default_val   = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    return (
        {"label": label, "options": options, "value": current_value, "key": widget_key,
         "disabled": disabled},
        current_value,
    )


@widget_component(ComponentType.SELECTBOX, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def selectbox(label: str, options: list, index: int = 0,
              key: str = None, disabled: bool = False, **kwargs) -> tuple[dict, str]:
    """Display a select dropdown. Returns the selected option string."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.SELECTBOX, label)
    default_val   = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    return (
        {"label": label, "options": options, "value": current_value, "key": widget_key,
         "disabled": disabled},
        current_value,
    )


@widget_component(ComponentType.TOGGLE, htmx=_HTMX_CLICK, oat=_OAT_FIELD)
def toggle(label: str, value: bool = False, key: str = None,
           disabled: bool = False) -> tuple[dict, bool]:
    """Display a toggle switch. Returns current on/off state."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.TOGGLE, label)
    state_val     = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@widget_component(ComponentType.COLOR_PICKER, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def color_picker(label: str, value: str = "#000000",
                 key: str = None, disabled: bool = False) -> tuple[dict, str]:
    """Display a color picker. Returns current hex color string."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.COLOR_PICKER, label)
    current_value = session_state.get(widget_key, value)
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@widget_component(ComponentType.DATE_INPUT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def date_input(label: str, value: str = "", key: str = None,
               disabled: bool = False) -> tuple[dict, str]:
    """Display a date input. Returns current date string (YYYY-MM-DD)."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.DATE_INPUT, label)
    current_value = session_state.get(widget_key, value)
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@widget_component(ComponentType.EMAIL_INPUT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def email_input(label: str, value: str = "", key: str = None,
                disabled: bool = False) -> tuple[dict, str]:
    """Display an email input with browser-native validation. Returns current value."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.EMAIL_INPUT, label)
    current_value = session_state.get(widget_key, value)
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@widget_component(ComponentType.PASSWORD_INPUT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def password_input(label: str, key: str = None,
                   disabled: bool = False) -> tuple[dict, str]:
    """Display a password input. Value is NEVER stored in session state."""
    widget_key = key or BaseComponent.generate_key(ComponentType.PASSWORD_INPUT, label)
    return ({"label": label, "value": "", "key": widget_key, "disabled": disabled}, "")


@widget_component(ComponentType.DATETIME_INPUT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def datetime_input(label: str, value: str = "", key: str = None,
                   disabled: bool = False) -> tuple[dict, str]:
    """Display a datetime-local input. Returns ISO datetime string."""
    widget_key    = key or BaseComponent.generate_key(ComponentType.DATETIME_INPUT, label)
    current_value = session_state.get(widget_key, value)
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


_HTMX_FILE = HtmxProps(trigger="change", encoding="multipart/form-data")


@widget_component(ComponentType.FILE_INPUT, htmx=_HTMX_FILE, oat=_OAT_FIELD)
def file_input(label: str, accept: str = "", key: str = None,
               disabled: bool = False) -> tuple[dict, str]:
    """Display a file upload input. Returns the uploaded filename.

    Args:
        label:    Field label.
        accept:   Comma-separated MIME types or extensions, e.g. ``'image/*'``.
        key:      Optional stable session-state key.
        disabled: If True, the input is non-interactive.
    """
    widget_key    = key or BaseComponent.generate_key(ComponentType.FILE_INPUT, label)
    current_value = session_state.get(widget_key, "")
    return ({"label": label, "accept": accept, "key": widget_key,
             "disabled": disabled}, current_value)


# ── New widgets ───────────────────────────────────────────────────────────────

@widget_component(ComponentType.MULTISELECT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def multiselect(label: str, options: list, default: list = None,
                key: str = None, disabled: bool = False) -> tuple[dict, list]:
    """Display a multi-select dropdown. Returns list of selected option strings.

    Args:
        label:    Field label.
        options:  List of option strings.
        default:  Initially selected options (default: empty list).
        key:      Optional stable session-state key.
        disabled: If True, the input is non-interactive.
    """
    widget_key = key or BaseComponent.generate_key(ComponentType.MULTISELECT, label)
    default    = default or []
    raw        = session_state.get(widget_key, default)
    # session_state may store a JSON string (from earlier runs) or a list
    if isinstance(raw, str):
        try:
            current_value = _json.loads(raw)
        except ValueError:
            current_value = [raw] if raw else []
    else:
        current_value = list(raw) if raw else []
    # Persist as JSON string so _coerce_form_value doesn't mangle it
    if isinstance(session_state.get(widget_key), list):
        session_state[widget_key] = current_value  # keep as list
    return (
        {"label": label, "options": options, "value": current_value,
         "key": widget_key, "disabled": disabled},
        current_value,
    )


@widget_component(ComponentType.SELECT_SLIDER, htmx=_HTMX_SLIDER, oat=_OAT_FIELD)
def select_slider(label: str, options: list, value=None,
                  key: str = None, disabled: bool = False) -> tuple[dict, object]:
    """Display a slider that snaps to discrete option values.

    Args:
        label:    Field label.
        options:  Ordered list of valid values (str, int, float).
        value:    Initially selected value (defaults to first option).
        key:      Optional stable session-state key.
        disabled: If True, the input is non-interactive.

    Returns the currently selected option value (same type as in ``options``).
    """
    widget_key    = key or BaseComponent.generate_key(ComponentType.SELECT_SLIDER, label)
    default_idx   = options.index(value) if value in options else 0
    stored        = session_state.get(widget_key, default_idx)
    try:
        current_idx = int(stored)
    except (ValueError, TypeError):
        current_idx = default_idx
    current_idx   = max(0, min(current_idx, len(options) - 1))
    current_value = options[current_idx]
    return (
        {"label": label, "options": options, "index": current_idx,
         "display_value": str(current_value), "key": widget_key, "disabled": disabled},
        current_value,
    )


@widget_component(ComponentType.TIME_INPUT, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def time_input(label: str, value: str = "", key: str = None,
               disabled: bool = False) -> tuple[dict, str]:
    """Display a time input. Returns current time string (HH:MM).

    Args:
        label:    Field label.
        value:    Default time in ``'HH:MM'`` format.
        key:      Optional stable session-state key.
        disabled: If True, the input is non-interactive.
    """
    widget_key    = key or BaseComponent.generate_key(ComponentType.TIME_INPUT, label)
    current_value = session_state.get(widget_key, value)
    return ({"label": label, "value": current_value, "key": widget_key,
             "disabled": disabled}, current_value)


@component(ComponentType.LINK_BUTTON)
def link_button(label: str, url: str, new_tab: bool = True) -> tuple[dict, None]:
    """Display a button-styled hyperlink (no HTMX, no session state).

    Args:
        label:   Button text.
        url:     Destination URL.
        new_tab: Open in a new browser tab (default True).
    """
    return ({"label": label, "url": url, "new_tab": new_tab}, None)


@component(ComponentType.DOWNLOAD_BUTTON)
def download_button(label: str, data: str | bytes, file_name: str,
                    mime: str = "text/plain") -> tuple[dict, None]:
    """Display a download button that triggers a client-side file download.

    Args:
        label:     Button text.
        data:      File content as ``str`` or ``bytes``.
        file_name: Suggested filename for the downloaded file.
        mime:      MIME type of the file (default ``'text/plain'``).
    """
    if isinstance(data, str):
        data = data.encode()
    b64 = base64.b64encode(data).decode()
    href = f"data:{mime};base64,{b64}"
    return ({"label": label, "href": href, "file_name": file_name}, None)


@widget_component(ComponentType.PILLS, htmx=_HTMX_CHANGE, oat=_OAT_FIELD)
def pills(label: str, options: list, index: int = 0,
          key: str = None, disabled: bool = False) -> tuple[dict, str]:
    """Display options as pill-shaped radio buttons. Returns selected option string.

    Args:
        label:    Field label / legend.
        options:  List of option strings.
        index:    Index of the initially selected option.
        key:      Optional stable session-state key.
        disabled: If True, all pills are non-interactive.
    """
    widget_key    = key or BaseComponent.generate_key(ComponentType.PILLS, label)
    default_val   = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    return (
        {"label": label, "options": options, "value": current_value,
         "key": widget_key, "disabled": disabled},
        current_value,
    )


@widget_component(ComponentType.FEEDBACK, htmx=HtmxProps(trigger="click"))
def feedback(label: str = "", sentiment: str = "thumbs",
             key: str = None) -> tuple[dict, str]:
    """Display a feedback widget. Returns the selected sentiment value.

    Args:
        label:     Optional label shown above the widget.
        sentiment: ``'thumbs'`` (👍/👎) or ``'stars'`` (1–5 ★).
        key:       Optional stable session-state key.

    Returns ``'up'`` / ``'down'`` for thumbs, ``'1'``–``'5'`` for stars,
    or ``''`` if nothing is selected yet.
    """
    widget_key    = key or BaseComponent.generate_key(ComponentType.FEEDBACK, label or sentiment)
    current_value = session_state.get(widget_key, "")
    if widget_key in session_state and current_value:
        # Reset after read so re-clicking toggles
        pass  # keep persistent (like Streamlit behaviour)
    return (
        {"label": label, "sentiment": sentiment, "value": current_value, "key": widget_key},
        current_value,
    )


@widget_component(ComponentType.PAGINATION, htmx=HtmxProps(trigger="click"))
def pagination(total_pages: int, current_page: int = 1, key: str = None) -> tuple[dict, int]:
    """Display page navigation buttons. Returns the currently selected page number (1-based).

    Clicking a page button triggers a full page re-render (same behaviour as
    ``mt.button``) so that the content driven by the page selection also updates.

    Args:
        total_pages:  Total number of pages.
        current_page: Initially selected page (default 1).
        key:          Optional stable session-state key.
    """
    widget_key    = key or BaseComponent.generate_key(ComponentType.PAGINATION, str(total_pages))
    current_value = int(session_state.get(widget_key, current_page))
    return (
        {"total_pages": total_pages, "current_page": current_value, "key": widget_key},
        current_value,
    )
