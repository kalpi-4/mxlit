from mxlit.context import get_context
from mxlit.state import session_state
import hashlib

def _generate_key(label: str, component_type: str) -> str:
    """Generate a unique key for a widget if one isn't provided."""
    return hashlib.md5(f"{component_type}-{label}".encode()).hexdigest()

def button(label: str, key: str = None) -> bool:
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
        
    if ctx:
        ctx.add_component({
            "type": "button",
            "label": label,
            "key": widget_key
        })
        
    return clicked

def text_input(label: str, value: str = "", key: str = None) -> str:
    """
    Display a single-line text input widget.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "text_input")
    
    # Get current value from session state, or use default
    current_value = session_state.get(widget_key, value)
    
    if ctx:
        ctx.add_component({
            "type": "text_input",
            "label": label,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def checkbox(label: str, value: bool = False, key: str = None) -> bool:
    """
    Display a checkbox widget.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "checkbox")
    
    # In HTML forms, an unchecked checkbox sends nothing. 
    # We need to handle this carefully in the server, or use a hidden input trick.
    # We'll assume the server puts "true" or "false" in the session state for us.
    state_val = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    
    if ctx:
        ctx.add_component({
            "type": "checkbox",
            "label": label,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def slider(label: str, min_value: int = 0, max_value: int = 100, value: int = None, key: str = None) -> int:
    """
    Display a slider widget.
    """
    ctx = get_context()
    widget_key = key or _generate_key(label, "slider")
    
    default_val = value if value is not None else min_value
    current_value = int(session_state.get(widget_key, default_val))
    
    if ctx:
        ctx.add_component({
            "type": "slider",
            "label": label,
            "min_value": min_value,
            "max_value": max_value,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def number_input(label: str, min_value=None, max_value=None, value=0, key: str = None, **kwargs):
    """Display a number input widget."""
    ctx = get_context()
    widget_key = key or _generate_key(label, "number_input")
    
    # Determine if we should use float or int based on inputs
    is_float = any(isinstance(v, float) for v in (min_value, max_value, value) if v is not None)
    type_cast = float if is_float else int
    
    current_value = type_cast(session_state.get(widget_key, value))
    
    if ctx:
        ctx.add_component({
            "type": "number_input",
            "label": label,
            "min_value": min_value,
            "max_value": max_value,
            "value": current_value,
            "step": kwargs.get("step"), # Add step support in template if desired later
            "key": widget_key
        })
        
    return current_value

def text_area(label: str, value: str = "", key: str = None) -> str:
    """Display a multi-line text input widget."""
    ctx = get_context()
    widget_key = key or _generate_key(label, "text_area")
    
    current_value = session_state.get(widget_key, value)
    
    if ctx:
        ctx.add_component({
            "type": "text_area",
            "label": label,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def radio(label: str, options: list, index: int = 0, key: str = None) -> str:
    """Display a radio button widget."""
    ctx = get_context()
    widget_key = key or _generate_key(label, "radio")
    
    default_val = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    
    if ctx:
        ctx.add_component({
            "type": "radio",
            "label": label,
            "options": options,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def selectbox(label: str, options: list, index: int = 0, key: str = None, **kwargs) -> str:
    """Display a select widget."""
    ctx = get_context()
    widget_key = key or _generate_key(label, "selectbox")
    
    default_val = options[index] if options and 0 <= index < len(options) else None
    current_value = session_state.get(widget_key, default_val)
    
    if ctx:
        ctx.add_component({
            "type": "selectbox",
            "label": label,
            "options": options,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def toggle(label: str, value: bool = False, key: str = None) -> bool:
    """Display a toggle switch widget."""
    ctx = get_context()
    widget_key = key or _generate_key(label, "toggle")
    
    state_val = session_state.get(widget_key, "true" if value else "false")
    current_value = state_val == "true"
    
    if ctx:
        ctx.add_component({
            "type": "toggle",
            "label": label,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def color_picker(label: str, value: str = "#000000", key: str = None) -> str:
    """Display a color picker widget."""
    ctx = get_context()
    widget_key = key or _generate_key(label, "color_picker")
    
    current_value = session_state.get(widget_key, value)
    
    if ctx:
        ctx.add_component({
            "type": "color_picker",
            "label": label,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value

def date_input(label: str, value: str = "", key: str = None) -> str:
    """Display a date input widget."""
    ctx = get_context()
    widget_key = key or _generate_key(label, "date_input")
    
    current_value = session_state.get(widget_key, value)
    
    if ctx:
        ctx.add_component({
            "type": "date_input",
            "label": label,
            "value": current_value,
            "key": widget_key
        })
        
    return current_value
