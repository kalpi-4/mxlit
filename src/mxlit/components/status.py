from mxlit.context import get_context

def error(body: str):
    """Display an error message."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "error", "content": body})
    else:
        print(f"[Error] {body}")

def warning(body: str):
    """Display a warning message."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "warning", "content": body})
    else:
        print(f"[Warning] {body}")

def info(body: str):
    """Display an informational message."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "info", "content": body})
    else:
        print(f"[Info] {body}")

def success(body: str):
    """Display a success message."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "status", "status_type": "success", "content": body})
    else:
        print(f"[Success] {body}")

def exception(e: Exception):
    """Display an exception."""
    ctx = get_context()
    body = f"{type(e).__name__}: {str(e)}"
    if ctx:
        ctx.add_component({"type": "status", "status_type": "error", "content": body})
    else:
        print(f"[Exception] {body}")
