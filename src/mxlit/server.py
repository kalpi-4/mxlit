import os
import runpy
from contextlib import asynccontextmanager
from pathlib import Path

import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mxlit._exceptions import RerunException
from mxlit._paths import STATIC_DIR, TEMPLATES_DIR
from mxlit.components.base import reset_render_counts
from mxlit.context import AppContext, _current_context
from mxlit.constants import THEME_KEY, theme_manager
from mxlit.state import session_state


def get_script_path() -> str:
    path = os.environ.get("MXLIT_SCRIPT")
    if not path or not Path(path).is_file():
        raise RuntimeError("MXLIT_SCRIPT environment variable not set or file not found.")
    return path


def _coerce_form_value(key: str, value: str) -> object:
    """Cast a form string value to match the type already stored in session_state."""
    if key not in session_state:
        return value
    old = session_state[key]
    if isinstance(old, int):
        try:
            return int(value)
        except ValueError:
            return value
    if isinstance(old, float):
        try:
            return float(value)
        except ValueError:
            return value
    if isinstance(old, bool):
        return str(value).lower() in ("true", "1", "yes", "on")
    return value


def _apply_form_data(form_data) -> None:
    """Write incoming form values into session_state with type coercion.

    Handles multi-value fields (e.g. <select multiple>) by collecting all
    values for a key into a list when more than one value is present.
    """
    seen: set[str] = set()
    for key in form_data:
        if key in seen:
            continue
        seen.add(key)
        values = form_data.getlist(key)
        if len(values) > 1:
            # Multi-select — store as list of strings
            session_state[key] = values
        else:
            session_state[key] = _coerce_form_value(key, values[0])


def _run_script(script_path: str) -> AppContext:
    """Execute the user script inside a fresh AppContext and return it."""
    reset_render_counts()
    ctx = AppContext()
    token = _current_context.set(ctx)
    try:
        runpy.run_path(script_path, run_name="__main__")
    except RerunException:
        pass
    except Exception as e:
        ctx.add_component({"type": "write", "content": f"Error executing script: {e}"})
    finally:
        _current_context.reset(token)
    return ctx


def _find_component(components: list, target_id: str) -> dict | None:
    """Recursively search the component tree for the component matching target_id."""
    for comp in components:
        if comp.get("id") == target_id:
            return comp
        found = _find_component(comp.get("children", []), target_id)
        if found:
            return found
    return None


# ── App setup ─────────────────────────────────────────────────────────────────

sse_clients: set = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    for queue in sse_clients:
        queue.put_nowait(None)


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.post("/interact", response_class=HTMLResponse)
async def interact(request: Request):
    """Handle HTMX interactions. Re-runs the script and returns updated HTML.

    When HX-Target is a component wrapper (starts with 'mx-'), returns only
    that component's fragment so HTMX can do a targeted outerHTML swap.
    Otherwise returns the full component tree.
    """
    form_data = await request.form()
    _apply_form_data(form_data)

    ctx = _run_script(get_script_path())

    # Targeted per-component swap (Section 10 — widget interactions)
    hx_target = request.headers.get("HX-Target", "")
    if hx_target.startswith("mx-"):
        target_id = hx_target[3:]  # strip "mx-" prefix
        comp = _find_component(ctx.components, target_id)
        if comp is not None:
            return templates.TemplateResponse(
                "component_fragment.html",
                {"request": request, "comp": comp, "theme": theme_manager.resolve()},
            )

    # Full render (initial load, button clicks, fallback)
    return templates.TemplateResponse(
        "components.html",
        {
            "request":     request,
            "components":  ctx.components,
            "theme":       theme_manager.resolve(),
            "main_class":  ctx.main_class,
            "aside_class": ctx.aside_class,
        },
    )


@app.post("/refresh/{component_id}", response_class=HTMLResponse)
async def refresh_component(request: Request, component_id: str):
    """Partial re-render for a single auto-refresh component (Section 11).

    Called by HTMX hx-trigger='every Ns' / 'load delay:Ns' on the component
    wrapper div. Re-runs the full user script, extracts the target component,
    and returns its HTML fragment. The client swaps via hx-swap='outerHTML'.
    """
    form_data = await request.form()
    _apply_form_data(form_data)

    ctx = _run_script(get_script_path())

    comp = _find_component(ctx.components, component_id)
    if comp is None:
        return HTMLResponse(f'<div id="mx-{component_id}"></div>')

    return templates.TemplateResponse(
        "component_fragment.html",
        {"request": request, "comp": comp, "theme": theme_manager.resolve()},
    )


@app.get("/events")
async def global_events(request: Request):
    """Global SSE endpoint for real-time updates pushed via /modify."""
    queue: asyncio.Queue = asyncio.Queue()
    sse_clients.add(queue)

    async def event_generator(req: Request):
        try:
            while True:
                if await req.is_disconnected():
                    break
                try:
                    html_str = await asyncio.wait_for(queue.get(), timeout=30.0)
                    if html_str is None:
                        yield "event: close\ndata: \n\n"
                        break
                    formatted = "\n".join(f"data: {line}" for line in html_str.split("\n"))
                    yield f"{formatted}\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            sse_clients.discard(queue)

    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/modify", response_class=JSONResponse)
async def modify_state(request: Request):
    """Modify state and push SSE update to all connected clients."""
    form_data = await request.form()
    _apply_form_data(form_data)

    ctx = _run_script(get_script_path())

    html_content = templates.get_template("components.html").render({
        "request":     request,
        "components":  ctx.components,
        "theme":       theme_manager.resolve(),
        "main_class":  ctx.main_class,
        "aside_class": ctx.aside_class,
    })

    for queue in sse_clients:
        queue.put_nowait(html_content)

    return JSONResponse(content={"status": "success"})


@app.get("/stream/{stream_id}")
async def stream_events(request: Request, stream_id: str):
    """SSE endpoint for text streaming (write_stream component)."""
    async def event_generator():
        stream_key = f"_stream_{stream_id}"
        if stream_key not in session_state:
            yield "event: close\ndata: \n\n"
            return
        stream = session_state[stream_key]
        try:
            for chunk in stream:
                if await request.is_disconnected():
                    break
                safe_chunk = str(chunk).replace("\n", " ")
                yield f"data: <span>{safe_chunk}</span>\n\n"
                await asyncio.sleep(0)
        finally:
            session_state.pop(stream_key, None)
        yield "event: close\ndata: \n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
