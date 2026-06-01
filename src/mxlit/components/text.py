import uuid
from typing import Callable

from mxlit.components.base import (
    BaseComponent, ComponentType, component,
)
from mxlit.state import session_state


# ── Heading factory ───────────────────────────────────────────────────────────

def _make_heading(component_type: ComponentType, fallback_prefix: str) -> Callable:
    """Generate a heading display function for the given heading level."""
    @component(component_type)
    def _fn(text: str) -> tuple[dict, Callable]:
        return (
            {"content": text},
            lambda: print(f"{fallback_prefix} {text}"),
        )
    _fn.__name__     = component_type.value
    _fn.__qualname__ = f"mxlit.components.text.{component_type.value}"
    return _fn


title     = _make_heading(ComponentType.TITLE,     "#")
header    = _make_heading(ComponentType.HEADER,    "##")
subheader = _make_heading(ComponentType.SUBHEADER, "###")


# ── Text components ───────────────────────────────────────────────────────────

@component(ComponentType.WRITE)
def write(*args) -> tuple[dict, Callable]:
    content = " ".join(str(a) for a in args)
    return ({"content": content}, lambda: print(content))


@component(ComponentType.TEXT)
def text(body: str) -> tuple[dict, Callable]:
    return ({"content": body}, lambda: print(body))


@component(ComponentType.MARKDOWN)
def markdown(body: str) -> tuple[dict, Callable]:
    try:
        import markdown as md
        html_content = md.markdown(body, extensions=["fenced_code", "tables"])
    except ImportError:
        html_content = f"<pre>{body}</pre>"
    return ({"content": html_content}, lambda: print(body))


@component(ComponentType.CODE)
def code(body: str) -> tuple[dict, Callable]:
    return ({"content": body}, lambda: print(body))


@component(ComponentType.HTML)
def html(body: str) -> tuple[dict, Callable]:
    return ({"content": body}, lambda: print(body))


@component(ComponentType.LATEX)
def latex(body: str) -> tuple[dict, Callable]:
    return ({"content": body}, lambda: print(f"LaTeX: {body}"))


@component(ComponentType.BADGE)
def badge(label: str) -> tuple[dict, Callable]:
    return ({"content": label}, lambda: print(f"Badge: {label}"))


@component(ComponentType.NER)
def ner_text(body: str, entities: list) -> tuple[dict, Callable]:
    return (
        {"content": body, "entities": entities},
        lambda: print(f"{body}\nEntities: {entities}"),
    )


# ── write_stream is display-only but needs session_state for the generator ────

@component(ComponentType.WRITE_STREAM)
def write_stream(stream) -> tuple[dict, Callable]:
    stream_id = str(uuid.uuid4())
    session_state[f"_stream_{stream_id}"] = stream
    return (
        {"stream_id": stream_id},
        lambda: [print(chunk, end="") for chunk in stream] or print(),
    )
