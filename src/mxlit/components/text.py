import uuid
from mxlit.context import get_context
from mxlit.state import session_state

def write(*args):
    """Print text or objects to the app."""
    ctx = get_context()
    if ctx:
        # Convert args to strings for simple rendering for now
        ctx.add_component({"type": "write", "content": " ".join(str(a) for a in args)})
    else:
        print(*args)

def title(text: str):
    """Display text in title formatting."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "title", "content": text})
    else:
        print(f"# {text}")

def header(text: str):
    """Display text in header formatting."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "header", "content": text})
    else:
        print(f"## {text}")

def subheader(text: str):
    """Display text in subheader formatting."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "subheader", "content": text})
    else:
        print(f"### {text}")

def text(text: str):
    """Display fixed-width text."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "text", "content": text})
    else:
        print(text)

def markdown(text: str):
    """Display text as markdown."""
    ctx = get_context()
    if ctx:
        try:
            import markdown as md
            html_content = md.markdown(text, extensions=['fenced_code', 'tables'])
        except ImportError:
            html_content = f"<pre>{text}</pre>"
        ctx.add_component({"type": "markdown", "content": html_content})
    else:
        print(text)

def code(text: str):
    """Display a code block."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "code", "content": text})
    else:
        print(text)
        
def html(text: str):
    """Display raw HTML."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "html", "content": text})
    else:
        print(text)

def latex(body: str):
    """Display mathematical expressions formatted as LaTeX."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "latex", "content": body})
    else:
        print(f"LaTeX: {body}")

def badge(label: str):
    """Display a badge."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "badge", "content": label})
    else:
        print(f"Badge: {label}")

def write_stream(stream):
    """Stream text to the app."""
    ctx = get_context()
    if ctx:
        stream_id = str(uuid.uuid4())
        session_state[f"_stream_{stream_id}"] = stream
        ctx.add_component({"type": "write_stream", "stream_id": stream_id})
    else:
        for chunk in stream:
            print(chunk, end="")
        print()

def ner_text(text: str, entities: list):
    """Display text with Named Entity Recognition highlights."""
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "ner", "content": text, "entities": entities})
    else:
        print(text)
        print("Entities:", entities)
