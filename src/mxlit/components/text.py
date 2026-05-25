import uuid
from mxlit.context import get_context
from mxlit.state import session_state

def write(*args, class_: str = ""):
    """Print text or objects to the app.

    Args:
        *args: Values to display, converted to strings and joined by spaces.
        class_: Optional Tailwind utility classes applied to the <p> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "write", "content": " ".join(str(a) for a in args), "class_": class_})
    else:
        print(*args)

def title(text: str, class_: str = ""):
    """Display text in title formatting.

    Args:
        text: The title string.
        class_: Optional Tailwind utility classes applied to the <h1> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "title", "content": text, "class_": class_})
    else:
        print(f"# {text}")

def header(text: str, class_: str = ""):
    """Display text in header formatting.

    Args:
        text: The header string.
        class_: Optional Tailwind utility classes applied to the <h2> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "header", "content": text, "class_": class_})
    else:
        print(f"## {text}")

def subheader(text: str, class_: str = ""):
    """Display text in subheader formatting.

    Args:
        text: The subheader string.
        class_: Optional Tailwind utility classes applied to the <h3> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "subheader", "content": text, "class_": class_})
    else:
        print(f"### {text}")

def text(text: str, class_: str = ""):
    """Display fixed-width text.

    Args:
        text: The text string.
        class_: Optional Tailwind utility classes applied to the <p> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "text", "content": text, "class_": class_})
    else:
        print(text)

def markdown(text: str, class_: str = ""):
    """Display text as markdown.

    Args:
        text: Markdown source string.
        class_: Optional Tailwind utility classes applied to the rendered <div>.
    """
    ctx = get_context()
    if ctx:
        try:
            import markdown as md
            html_content = md.markdown(text, extensions=['fenced_code', 'tables'])
        except ImportError:
            html_content = f"<pre>{text}</pre>"
        ctx.add_component({"type": "markdown", "content": html_content, "class_": class_})
    else:
        print(text)

def code(text: str, class_: str = ""):
    """Display a code block.

    Args:
        text: The source code string.
        class_: Optional Tailwind utility classes applied to the <pre> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "code", "content": text, "class_": class_})
    else:
        print(text)

def html(text: str, class_: str = ""):
    """Display raw HTML.

    Args:
        text: Raw HTML string.
        class_: Optional Tailwind utility classes applied to the wrapper <div>.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "html", "content": text, "class_": class_})
    else:
        print(text)

def latex(body: str, class_: str = ""):
    """Display mathematical expressions formatted as LaTeX.

    Args:
        body: LaTeX source string (without surrounding $$).
        class_: Optional Tailwind utility classes applied to the wrapper <div>.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "latex", "content": body, "class_": class_})
    else:
        print(f"LaTeX: {body}")

def badge(label: str, class_: str = ""):
    """Display a badge.

    Args:
        label: Badge text.
        class_: Optional Tailwind utility classes applied to the <span> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "badge", "content": label, "class_": class_})
    else:
        print(f"Badge: {label}")

def write_stream(stream, class_: str = ""):
    """Stream text to the app.

    Args:
        stream: A generator or iterable that yields text chunks.
        class_: Optional Tailwind utility classes applied to the stream container.
    """
    ctx = get_context()
    if ctx:
        stream_id = str(uuid.uuid4())
        session_state[f"_stream_{stream_id}"] = stream
        ctx.add_component({"type": "write_stream", "stream_id": stream_id, "class_": class_})
    else:
        for chunk in stream:
            print(chunk, end="")
        print()

def ner_text(text: str, entities: list, class_: str = ""):
    """Display text with Named Entity Recognition highlights.

    Args:
        text: The source text string.
        entities: List of entity dicts with 'start', 'end', and 'label' keys.
        class_: Optional Tailwind utility classes applied to the outer <div>.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "ner", "content": text, "entities": entities, "class_": class_})
    else:
        print(text)
        print("Entities:", entities)
