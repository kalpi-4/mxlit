import contextvars

# Global context variable to store the current app context during a script run
_current_context = contextvars.ContextVar('current_context')

class AppContext:
    def __init__(self):
        self.components = []
        # Current target list for adding components. Changes when inside a container 'with' block.
        self.current_target = self.components

    def add_component(self, component):
        """Append a component dictionary to the current target list."""
        self.current_target.append(component)

def get_context():
    """Retrieve the current AppContext, or None if not within a script run."""
    try:
        return _current_context.get()
    except LookupError:
        return None
