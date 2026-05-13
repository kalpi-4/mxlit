from mxlit.context import get_context

class ContainerContextManager:
    """
    A context manager that captures all components created within its `with` block
    and appends them as children to a container component.
    """
    def __init__(self, container_type: str, **kwargs):
        from mxlit.layout import layout_manager
        self.container_type = container_type
        self.kwargs = kwargs
        self.layout_manager = layout_manager
        self.container_id = None
        self.parent_children_list = None
        self._added_to_parent = False

    def __enter__(self):
        ctx = get_context()
        if ctx:
            if ctx.mode == "init":
                # Use LayoutManager for schema building
                self.container_id = self.layout_manager.start_container(
                    self.container_type, self.kwargs
                )
            else:
                # Legacy runtime mode
                self.container_component = {
                    "type": self.container_type,
                    "children": [],
                    **self.kwargs
                }
                # Save the current target list where components are being added
                if self.parent_children_list is None:
                    self.parent_children_list = ctx.current_target
                # Change the target list to our own children list
                ctx.current_target = self.container_component["children"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ctx = get_context()
        if ctx:
            if ctx.mode == "init":
                # End container in LayoutManager
                self.layout_manager.end_container()
            else:
                # Legacy runtime mode
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

class _TabContextManager:
    """Context manager for a single tab within a tabs group."""

    def __init__(self, label: str, parent_id: str):
        from mxlit.layout import layout_manager
        self.label = label
        self.parent_id = parent_id
        self.layout_manager = layout_manager
        self.tab_id = None

    def __enter__(self):
        # Push the parent tabs group onto the stack so this tab becomes its child
        self.layout_manager.current_container_stack.append(self.parent_id)
        self.tab_id = self.layout_manager.start_container("tab", {"label": self.label})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.layout_manager.end_container()
        # Pop the temporarily pushed parent
        if (self.layout_manager.current_container_stack and
                self.layout_manager.current_container_stack[-1] == self.parent_id):
            self.layout_manager.current_container_stack.pop()


def tabs(tabs_spec):
    """
    Create a set of tabs.
    `tabs_spec` is a list of strings (tab labels).
    Returns a list of container context managers.
    """
    from mxlit.context import get_context
    from mxlit.layout import layout_manager

    ctx = get_context()
    tab_containers = []

    if ctx and ctx.mode == "init":
        # Register a parent "tabs" wrapper so the template can render a proper tab UI
        tabs_group_id = layout_manager.register_component("tabs", {})
        for label in tabs_spec:
            tab_containers.append(_TabContextManager(label, tabs_group_id))
    else:
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
