from mxlit.context import get_context
from mxlit.state import session_state
from mxlit.layout import layout_manager
import hashlib

def _generate_key(label: str, component_type: str) -> str:
    """Generate a unique key for a widget if one isn't provided."""
    return hashlib.md5(f"{component_type}-{label}".encode()).hexdigest()


def _register_component(component_type: str, props: dict, key: str, id: str = None):
    """
    Helper to register component based on context mode.
    Returns component_id in init mode, None in runtime mode.
    """
    ctx = get_context()
    if ctx:
        if ctx.mode == "init":
            # Add key to props for template rendering
            props_with_key = {**props, "key": key}
            component_id = layout_manager.register_component(
                component_type,
                props_with_key,
                component_id=id
            )
            return component_id
        else:
            ctx.add_component({
                "type": component_type,
                "key": key,
                **props
            })
    return None

def button(label: str, key: str = None, id: str = None) -> bool:
    """
    Display a button widget.
    Returns True if the button was clicked on the last run, False otherwise.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "button")

    # Buttons are ephemeral - they are true only for the request where they were clicked.
    # In HTMX, if the button was clicked, its name/value will be in the form data.
    clicked = session_state.get(widget_key, "false") == "true"

    # We must reset the button state so it doesn't stay True on subsequent unrelated reruns
    if widget_key in session_state:
        session_state[widget_key] = "false"

    _register_component("button", {"label": label}, widget_key, id)

    ctx = get_context()
    if ctx and ctx.mode == "init":
        # During schema building buttons are never "clicked"; always return False
        # so that `if mt.button("X"):` blocks are skipped during init.
        return False

    return clicked

def text_input(label: str, value: str = "", key: str = None, id: str = None) -> str:
    """
    Display a single-line text input widget.
    """
    widget_key = key or _generate_key(label, "text_input")

    # Get current value from session state, or use default
    current_value = session_state.get(widget_key, value)

    _register_component("text_input", {
        "label": label,
        "value": current_value
    }, widget_key, id)

    return current_value

def checkbox(label: str, value: bool = False, key: str = None) -> bool:
    """
    Display a checkbox widget.
    """
    widget_key = key or _generate_key(label, "checkbox")
    
    state_val = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    
    _register_component("checkbox", {
        "label": label,
        "value": current_value
    }, widget_key)
        
    return current_value

def slider(label: str, min_value: int = 0, max_value: int = 100, value: int = None, key: str = None) -> int:
    """
    Display a slider widget.
    """
    widget_key = key or _generate_key(label, "slider")
    
    default_val = value if value is not None else min_value
    current_value = int(session_state.get(widget_key, default_val))
    
    _register_component("slider", {
        "label": label,
        "min_value": min_value,
        "max_value": max_value,
        "value": current_value
    }, widget_key)
        
    return current_value

def number_input(label: str, min_value=None, max_value=None, value=0, key: str = None, **kwargs):
    """Display a number input widget."""
    widget_key = key or _generate_key(label, "number_input")
    
    # Determine if we should use float or int based on inputs
    is_float = any(isinstance(v, float) for v in (min_value, max_value, value) if v is not None)
    type_cast = float if is_float else int
    
    current_value = type_cast(session_state.get(widget_key, value))
    
    _register_component("number_input", {
        "label": label,
        "min_value": min_value,
        "max_value": max_value,
        "value": current_value,
        "step": kwargs.get("step")
    }, widget_key)
        
    return current_value

def text_area(label: str, value: str = "", key: str = None) -> str:
    """Display a multi-line text input widget."""
    widget_key = key or _generate_key(label, "text_area")
    
    current_value = session_state.get(widget_key, value)
    
    _register_component("text_area", {
        "label": label,
        "value": current_value
    }, widget_key)
        
    return current_value

def radio(label: str, options: list, index: int = 0, key: str = None) -> str:
    """Display a radio button widget."""
    widget_key = key or _generate_key(label, "radio")
    
    default_val = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    
    _register_component("radio", {
        "label": label,
        "options": options,
        "value": current_value
    }, widget_key)
        
    return current_value

def selectbox(label: str, options: list, index: int = 0, key: str = None, id: str = None, **kwargs) -> str:
    """Display a select widget."""
    widget_key = key or _generate_key(label, "selectbox")

    default_val = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)

    _register_component("selectbox", {
        "label": label,
        "options": options,
        "value": current_value
    }, widget_key, id)

    return current_value

def toggle(label: str, value: bool = False, key: str = None) -> bool:
    """Display a toggle switch widget."""
    widget_key = key or _generate_key(label, "toggle")
    
    state_val = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    
    _register_component("toggle", {
        "label": label,
        "value": current_value
    }, widget_key)
        
    return current_value

def color_picker(label: str, value: str = "#000000", key: str = None) -> str:
    """Display a color picker widget."""
    widget_key = key or _generate_key(label, "color_picker")
    
    current_value = session_state.get(widget_key, value)
    
    _register_component("color_picker", {
        "label": label,
        "value": current_value
    }, widget_key)
        
    return current_value

def date_input(label: str, value: str = "", key: str = None) -> str:
    """Display a date input widget."""
    widget_key = key or _generate_key(label, "date_input")
    
    current_value = session_state.get(widget_key, value)
    
    _register_component("date_input", {
        "label": label,
        "value": current_value
    }, widget_key)
        
    return current_value
