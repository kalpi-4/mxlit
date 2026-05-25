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

    def __call__(self, class_: str = ""):
        """Allow ``with mt.sidebar(class_="w-80 bg-slate-50"):`` syntax.

        Returns a fresh :class:`ContainerContextManager` for the sidebar so
        that Tailwind utility classes can be applied to the ``<aside>`` element.
        """
        return ContainerContextManager("sidebar", class_=class_)

    def __enter__(self):
        self.parent_children_list = None
        self._added_to_parent = False
        self.container_component = {
            "type": "sidebar",
            "children": [],
            "class_": "",
        }
        return super().__enter__()

sidebar = Sidebar()

def columns(spec, vertical_alignment="top", class_: str = ""):
    """Create a set of columns.

    ``spec`` can be an integer (number of equal columns) or an iterable of
    relative weights.  Returns a list of context managers — one per column.

    Args:
        spec: Number of equal columns (int) or list of relative weights.
        vertical_alignment: ``"top"`` (default), ``"center"``, or ``"bottom"``.
        class_: Optional Tailwind utility classes applied to the outer columns
            wrapper ``<div>`` (e.g. ``"gap-8 items-start"``).
    """
    if isinstance(spec, int):
        weights = [1] * spec
    else:
        weights = list(spec)

    cols = []
    for w in weights:
        cols.append(ContainerContextManager(
            "column", weight=w, columns_class_=class_,
            vertical_alignment=vertical_alignment,
        ))
    return cols

def tabs(tabs_spec, class_: str = ""):
    """Create a set of tabs.

    Args:
        tabs_spec: List of tab label strings.
        class_: Optional Tailwind utility classes applied to the outer
            ``<ot-tabs>`` wrapper element.
    """
    tab_containers = []
    for label in tabs_spec:
        tab_containers.append(
            ContainerContextManager("tab", label=label, tabs_class_=class_)
        )
    return tab_containers

def expander(label: str, icon: str = None, class_: str = ""):
    """Create an expandable container.

    Args:
        label: The expander heading text.
        icon: Optional icon shown beside the heading.
        class_: Optional Tailwind utility classes applied to the <details> element.
    """
    return ContainerContextManager("expander", label=label, icon=icon, class_=class_)

def container(horizontal: bool = False, class_: str = ""):
    """Create a general-purpose container.

    Args:
        horizontal: If True, children are laid out in a horizontal row.
        class_: Optional Tailwind utility classes applied to the container <div>.
    """
    return ContainerContextManager("container", horizontal=horizontal, class_=class_)

def page_config(main_class: str = "", aside_class: str = ""):
    """Set extra Tailwind utility classes on the top-level layout elements.

    Must be called before any component is rendered (typically at the top of
    the script).  The classes are **additive** — they are appended to the
    element's existing base classes (``mx-main`` for the main area and oat.ink
    sidebar classes for the aside).

    Args:
        main_class: Classes applied to ``<main class="mx-main …">``.
            Example: ``"max-w-6xl mx-auto px-8"``.
        aside_class: Classes applied to ``<aside data-sidebar …>``.
            Example: ``"w-72 bg-slate-900 text-slate-100"``.
            This is merged with any ``class_`` already passed to
            ``mt.sidebar(class_="…")``.

    Example::

        mt.page_config(
            main_class="max-w-5xl mx-auto px-6 py-4",
            aside_class="w-72",
        )
    """
    ctx = get_context()
    if ctx:
        ctx.main_class = main_class
        ctx.aside_class = aside_class
