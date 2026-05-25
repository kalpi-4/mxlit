from mxlit.context import get_context

def error(body: str, class_: str = ""):
    """Display an error message.

    Args:
        body: The error text.
        class_: Optional Tailwind utility classes applied to the alert element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "error", "content": body, "class_": class_})
    else:
        print(f"[Error] {body}")

def warning(body: str, class_: str = ""):
    """Display a warning message.

    Args:
        body: The warning text.
        class_: Optional Tailwind utility classes applied to the alert element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "warning", "content": body, "class_": class_})
    else:
        print(f"[Warning] {body}")

def info(body: str, class_: str = ""):
    """Display an informational message.

    Args:
        body: The info text.
        class_: Optional Tailwind utility classes applied to the alert element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "info", "content": body, "class_": class_})
    else:
        print(f"[Info] {body}")

def success(body: str, class_: str = ""):
    """Display a success message.

    Args:
        body: The success text.
        class_: Optional Tailwind utility classes applied to the alert element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "success", "content": body, "class_": class_})
    else:
        print(f"[Success] {body}")

def exception(e: Exception, class_: str = ""):
    """Display an exception as an error alert.

    Args:
        e: The exception instance to display.
        class_: Optional Tailwind utility classes applied to the alert element.
    """
    ctx = get_context()
    body = f"{type(e).__name__}: {str(e)}"
    if ctx:
        ctx.add_component({"type": "status", "status_type": "error", "content": body, "class_": class_})
    else:
        print(f"[Exception] {body}")
