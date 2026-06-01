import contextvars

_current_context = contextvars.ContextVar('current_context')

class AppContext:
    def __init__(self):
        self.components = []
        self.current_target = self.components
        self.main_class: str = ""
        self.aside_class: str = ""
        self._auto_refresh: str | None = None  # set by setInterval/setTimeout context managers

    def add_component(self, component: dict) -> None:
        """Append a component dict to the current target list.

        When an auto-refresh context is active, injects 'refresh_trigger' into
        the component so the template can emit the HTMX polling attributes.
        """
        if self._auto_refresh is not None:
            component = {**component, "refresh_trigger": self._auto_refresh}
        self.current_target.append(component)


def get_context():
    """Retrieve the current AppContext, or None if not within a script run."""
    try:
        return _current_context.get()
    except LookupError:
        return None
