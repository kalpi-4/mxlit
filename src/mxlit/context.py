import contextvars

# Global context variable to store the current app context during a script run
_current_context = contextvars.ContextVar('current_context')

class AppContext:
    def __init__(self, mode="runtime"):
        """
        mode: "init" for schema building, "runtime" for backward compatibility rendering
        """
        self.mode = mode
        if mode == "runtime":
            self.components = []
            # Current target list for adding components. Changes when inside a container 'with' block.
            self.current_target = self.components
        else:  # init mode
            self.components = None
            self.current_target = None

    def add_component(self, component):
        """Append a component dictionary to the current target list."""
        if self.mode == "runtime":
            self.current_target.append(component)
        else:
            from mxlit.layout import layout_manager
            component_type = component.get("type")
            props = {k: v for k, v in component.items() if k != "type"}
            layout_manager.register_component(component_type, props)

def get_context():
    """Retrieve the current AppContext, or None if not within a script run."""
    try:
        return _current_context.get()
    except LookupError:
        return None
