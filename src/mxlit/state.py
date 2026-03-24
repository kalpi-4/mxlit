class SessionState:
    """
    A dictionary-like object that allows attribute access to session state variables.
    This mimics Streamlit's st.session_state behavior.
    """
    def __init__(self):
        super().__setattr__('_state', {})

    def __getattr__(self, name):
        if name in self._state:
            return self._state[name]
        raise AttributeError(f"st.session_state has no attribute '{name}'")

    def __setattr__(self, name, value):
        self._state[name] = value

    def __contains__(self, name):
        return name in self._state

    def __getitem__(self, name):
        return self._state[name]

    def __setitem__(self, name, value):
        self._state[name] = value

    def get(self, name, default=None):
        return self._state.get(name, default)

    def update(self, **kwargs):
        self._state.update(kwargs)

    def clear(self):
        self._state.clear()

# Global session state (in a real multi-user setup, this would be tied to a session ID)
# For the initial execution engine step, a single global instance works.
session_state = SessionState()
