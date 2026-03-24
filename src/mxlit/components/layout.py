from mxlit.context import get_context

class ContainerContextManager:
    """
    A context manager that captures all components created within its `with` block
    and appends them as children to a container component.
    """
    def __init__(self, container_type: str, **kwargs):
        self.container_type = container_type
        self.kwargs = kwargs
        self.container_component = {
            "type": container_type,
            "children": [],
            **kwargs
        }
        self.parent_children_list = None
        self._added_to_parent = False
        
    def __enter__(self):
        ctx = get_context()
        if ctx:
            # Save the current target list where components are being added
            if self.parent_children_list is None:
                self.parent_children_list = ctx.current_target
            # Change the target list to our own children list
            ctx.current_target = self.container_component["children"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ctx = get_context()
        if ctx:
            # Restore the parent's target list
            ctx.current_target = self.parent_children_list
            # Add ourselves to the parent's target list
            if not self._added_to_parent:
                ctx.add_component(self.container_component)
                self._added_to_parent = True

    def __getattr__(self, name):
        import mxlit as mt
        if hasattr(mt, name):
            func = getattr(mt, name)
            if callable(func):
                def wrapper(*args, **kwargs):
                    with self:
                        return func(*args, **kwargs)
                return wrapper
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class Sidebar(ContainerContextManager):
    def __init__(self):
        super().__init__("sidebar")

    def __enter__(self):
        # We need a new container instance for each enter since sidebar is instantiated once globally
        self.container_component = {
            "type": "sidebar",
            "children": [],
        }
        return super().__enter__()

sidebar = Sidebar()

def columns(spec, vertical_alignment="top"):
    """
    Create a set of columns. 
    `spec` can be an integer (number of equal columns) or an iterable of weights.
    Returns a list of container context managers.
    """
    if isinstance(spec, int):
        weights = [1] * spec
    else:
        weights = list(spec)
        
    cols = []
    # We wrap columns in a 'columns' container in the DOM eventually
    for w in weights:
        cols.append(ContainerContextManager("column", weight=w))
        
    # Hack: To render them together correctly, we could just return the list.
    # In a real impl, we'd need a master 'columns' container that holds them.
    # We'll just return the context managers and let the user do `with col1:`
    return cols

def tabs(tabs_spec):
    """
    Create a set of tabs.
    `tabs_spec` is a list of strings (tab labels).
    Returns a list of container context managers.
    """
    tab_containers = []
    for label in tabs_spec:
        tab_containers.append(ContainerContextManager("tab", label=label))
    return tab_containers

def expander(label: str, icon: str = None):
    """
    Create an expandable container.
    """
    return ContainerContextManager("expander", label=label, icon=icon)

def container(horizontal: bool = False):
    """
    Create a general container.
    """
    return ContainerContextManager("container", horizontal=horizontal)
