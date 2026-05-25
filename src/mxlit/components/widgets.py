from mxlit.context import get_context
from mxlit.state import session_state
import hashlib

def _generate_key(label: str, component_type: str) -> str:
    """Generate a unique key for a widget if one isn't provided."""
    return hashlib.md5(f"{component_type}-{label}".encode()).hexdigest()

def button(label: str, key: str = None, class_: str = "") -> bool:
    """Display a button widget. Returns True if clicked on this run.

    Args:
        label: Button text.
        key: Optional unique key. Auto-generated from label when omitted.
        class_: Optional Tailwind utility classes applied to the <button> element.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "button")
    clicked = session_state.get(widget_key, "false") == "true"
    if widget_key in session_state:
        session_state[widget_key] = "false"
    if ctx:
        ctx.add_component({"type": "button", "label": label, "key": widget_key, "class_": class_})
    return clicked

def text_input(label: str, value: str = "", key: str = None, class_: str = "") -> str:
    """Display a single-line text input widget.

    Args:
        label: Field label.
        value: Default value.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "text_input")
    current_value = session_state.get(widget_key, value)
    if ctx:
        ctx.add_component({"type": "text_input", "label": label, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value

def checkbox(label: str, value: bool = False, key: str = None, class_: str = "") -> bool:
    """Display a checkbox widget.

    Args:
        label: Checkbox label.
        value: Default checked state.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "checkbox")
    state_val = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    if ctx:
        ctx.add_component({"type": "checkbox", "label": label, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value

def slider(label: str, min_value: int = 0, max_value: int = 100,
           value: int = None, key: str = None, class_: str = "") -> int:
    """Display a slider widget.

    Args:
        label: Slider label.
        min_value: Minimum value.
        max_value: Maximum value.
        value: Default value (defaults to min_value).
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "slider")
    default_val = value if value is not None else min_value
    current_value = int(session_state.get(widget_key, default_val))
    if ctx:
        ctx.add_component({"type": "slider", "label": label, "min_value": min_value,
                           "max_value": max_value, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value

def number_input(label: str, min_value=None, max_value=None, value=0,
                 key: str = None, class_: str = "", **kwargs):
    """Display a number input widget.

    Args:
        label: Field label.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.
        value: Default value.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "number_input")
    is_float = any(isinstance(v, float) for v in (min_value, max_value, value) if v is not None)
    type_cast = float if is_float else int
    current_value = type_cast(session_state.get(widget_key, value))
    if ctx:
        ctx.add_component({"type": "number_input", "label": label, "min_value": min_value,
                           "max_value": max_value, "value": current_value,
                           "step": kwargs.get("step"), "key": widget_key, "class_": class_})
    return current_value

def text_area(label: str, value: str = "", key: str = None, class_: str = "") -> str:
    """Display a multi-line text input widget.

    Args:
        label: Field label.
        value: Default text content.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "text_area")
    current_value = session_state.get(widget_key, value)
    if ctx:
        ctx.add_component({"type": "text_area", "label": label, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value

def radio(label: str, options: list, index: int = 0,
          key: str = None, class_: str = "") -> str:
    """Display a radio button group.

    Args:
        label: Group label.
        options: List of option strings.
        index: Default selected index.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <fieldset>.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "radio")
    default_val = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    if ctx:
        ctx.add_component({"type": "radio", "label": label, "options": options,
                           "value": current_value, "key": widget_key, "class_": class_})
    return current_value

def selectbox(label: str, options: list, index: int = 0,
              key: str = None, class_: str = "", **kwargs) -> str:
    """Display a select (dropdown) widget.

    Args:
        label: Field label.
        options: List of option strings.
        index: Default selected index.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <div data-field> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "selectbox")
    default_val = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    if ctx:
        ctx.add_component({"type": "selectbox", "label": label, "options": options,
                           "value": current_value, "key": widget_key, "class_": class_})
    return current_value

def toggle(label: str, value: bool = False, key: str = None, class_: str = "") -> bool:
    """Display a toggle switch widget.

    Args:
        label: Toggle label.
        value: Default on/off state.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "toggle")
    state_val = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    if ctx:
        ctx.add_component({"type": "toggle", "label": label, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value

def color_picker(label: str, value: str = "#000000",
                 key: str = None, class_: str = "") -> str:
    """Display a color picker widget.

    Args:
        label: Field label.
        value: Default hex color string.
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "color_picker")
    current_value = session_state.get(widget_key, value)
    if ctx:
        ctx.add_component({"type": "color_picker", "label": label, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value

def date_input(label: str, value: str = "", key: str = None, class_: str = "") -> str:
    """Display a date input widget.

    Args:
        label: Field label.
        value: Default date string (YYYY-MM-DD).
        key: Optional unique key.
        class_: Optional Tailwind utility classes applied to the <label> wrapper.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "date_input")
    current_value = session_state.get(widget_key, value)
    if ctx:
        ctx.add_component({"type": "date_input", "label": label, "value": current_value,
                           "key": widget_key, "class_": class_})
    return current_value
