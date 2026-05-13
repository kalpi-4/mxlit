import os
import sys
import runpy
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio

from mxlit.context import AppContext, _current_context
from mxlit.state import session_state
from mxlit.layout import layout_manager
from mxlit.callbacks import callback_registry
from mxlit.dag import reactive_dag

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Initialize app schema
    try:
        script_path = get_script_path()
        ctx = AppContext(mode="init")
        token = _current_context.set(ctx)
        try:
            # Run script in init mode to build layout schema and register callbacks
            runpy.run_path(script_path, run_name="__main__")
        except Exception as e:
            if type(e).__name__ not in ("RerunException", "SystemExit"):
                raise
        finally:
            _current_context.reset(token)

        # Build DAG from registered callbacks
        for callback_id, callback_info in callback_registry.get_all_callbacks().items():
            reactive_dag.register_callback(
                callback_id,
                callback_info["inputs"],
                callback_info["outputs"]
            )

    except Exception as e:
        print(f"Error during app initialization: {e}")

    yield

    # Shutdown logic: Cancel all active SSE connections
    for queue in sse_clients:
        queue.put_nowait(None)  # Send sentinel value to stop generator

app = FastAPI(lifespan=lifespan)

sse_clients = set()

# Setup static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def get_script_path():
    path = os.environ.get("MXLIT_SCRIPT")
    if not path or not Path(path).is_file():
        raise RuntimeError("MXLIT_SCRIPT environment variable not set or file not found.")
    return path

def rebuild_layout_schema():
    layout_manager.components.clear()
    layout_manager.root_children.clear()
    layout_manager.current_container_stack.clear()
    layout_manager.next_geometry = {"x": 0, "y": 0, "width": 12, "height": 1}

    script_path = get_script_path()
    ctx = AppContext(mode="init")
    token = _current_context.set(ctx)
    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        # RerunException (and SystemExit from mt.stop()) are expected control flow;
        # ignore them so the partial schema that was built up to that point is used.
        if type(e).__name__ not in ("RerunException", "SystemExit"):
            raise
    finally:
        _current_context.reset(token)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the initial app shell."""
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/initial", response_class=HTMLResponse)
async def get_initial_layout(request: Request):
    """Serve the initial layout using the pre-built schema."""
    layout_schema = layout_manager.get_layout_schema()
    return templates.TemplateResponse(
        "components.html",
        {"request": request, "layout_schema": layout_schema}
    )

@app.post("/interact", response_class=HTMLResponse)
async def interact(request: Request):
    """
    Handle HTMX interactions using reactive DAG execution.
    """
    form_data = await request.form()

    # Track changed inputs for DAG
    changed_inputs = set()

    for key, value in form_data.items():
        # Try to cast value to existing type if it exists in session_state
        old_value = session_state.get(key)
        if key in session_state:
            if isinstance(old_value, int):
                try:
                    value = int(value)
                except ValueError:
                    pass
            elif isinstance(old_value, float):
                try:
                    value = float(value)
                except ValueError:
                    pass
            elif isinstance(old_value, bool):
                # Handle boolean casting
                if str(value).lower() in ("true", "1", "yes", "on"):
                    value = True
                elif str(value).lower() in ("false", "0", "no", "off"):
                    value = False

        # Only mark as changed if value actually changed
        if session_state.get(key) != value:
            changed_inputs.add(key)

        session_state[key] = value

    # Mark dirty inputs in DAG
    for input_key in changed_inputs:
        reactive_dag.mark_input_dirty(input_key)

    # Execute affected callbacks
    try:
        updates = await reactive_dag.execute_callbacks(callback_registry, session_state)

        # Send targeted updates via SSE
        if updates:
            # Format: component_id:html_fragment
            update_messages = []
            for component_id, new_value in updates.items():
                update_messages.append(f"{component_id}\t{new_value}")

            sse_message = "\n".join(update_messages)
            for queue in sse_clients:
                queue.put_nowait(sse_message)

        # Rebuild and re-render full layout with updated state and return HTML for HTMX swap
        rebuild_layout_schema()
        layout_schema = layout_manager.get_layout_schema()
        html = templates.get_template("components.html").render(
            request=request, 
            layout_schema=layout_schema
        )
        return HTMLResponse(content=html, status_code=200)

    except Exception as e:
        return HTMLResponse(content=f"<div>Error: {e}</div>", status_code=500)

@app.get("/events")
async def global_events(request: Request):
    """
    Global SSE endpoint for real-time updates.
    """
    queue = asyncio.Queue()
    sse_clients.add(queue)
    
    async def event_generator(req: Request):
        try:
            while True:
                # Use wait_for to periodically check if the client disconnected
                # If they did, we raise an exception/break.
                if await req.is_disconnected():
                    break
                    
                try:
                    # Wait for next event or connection close, with a short timeout
                    html_str = await asyncio.wait_for(queue.get(), timeout=1.0)
                    
                    if html_str is None:
                        # Send a final empty payload to close SSE cleanly before server exits
                        yield "event: close\ndata: \n\n"
                        break
                    # Yield it in SSE format, being careful with newlines.
                    # Since html_str can contain newlines, we should format it properly for SSE.
                    formatted_data = "\n".join(f"data: {line}" for line in html_str.split("\n"))
                    yield f"event: targetedUpdate\n{formatted_data}\n\n"
                except asyncio.TimeoutError:
                    # Just keep checking
                    continue
        except asyncio.CancelledError:
            pass
        finally:
            sse_clients.discard(queue)

    return StreamingResponse(event_generator(request), media_type="text/event-stream")

@app.post("/modify", response_class=JSONResponse)
async def modify_state(request: Request):
    """
    Modify state and push targeted updates to all connected clients.
    """
    form_data = await request.form()

    # Track changed inputs
    changed_inputs = set()

    for key, value in form_data.items():
        # Try to cast value to existing type
        old_value = session_state.get(key)
        if key in session_state:
            if isinstance(old_value, int):
                try:
                    value = int(value)
                except ValueError:
                    pass
            elif isinstance(old_value, float):
                try:
                    value = float(value)
                except ValueError:
                    pass
            elif isinstance(old_value, bool):
                if str(value).lower() in ("true", "1", "yes", "on"):
                    value = True
                elif str(value).lower() in ("false", "0", "no", "off"):
                    value = False

        if session_state.get(key) != value:
            changed_inputs.add(key)

        session_state[key] = value

    # Mark dirty inputs and execute callbacks
    for input_key in changed_inputs:
        reactive_dag.mark_input_dirty(input_key)

    try:
        updates = await reactive_dag.execute_callbacks(callback_registry, session_state)

        # Convert updates to targeted SSE messages
        # Format: component_id:html_fragment
        update_messages = []
        for component_id, new_value in updates.items():
            update_messages.append(f"{component_id}\t{new_value}")

        # Send targeted updates via SSE
        sse_message = "\n".join(update_messages)
        for queue in sse_clients:
            queue.put_nowait(sse_message)

        return JSONResponse(content={"status": "success", "updates": list(updates.keys())})

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.get("/stream/{stream_id}")
async def stream_events(stream_id: str):
    """
    Handle SSE for text streaming.
    """
    async def event_generator():
        stream_key = f"_stream_{stream_id}"
        if stream_key in session_state:
            # We assume it's a generator or iterable
            stream = session_state[stream_key]
            for chunk in stream:
                # SSE format: data: <content>\n\n
                # We can sleep a tiny bit to make it look like streaming if it's too fast
                # but let's let the generator handle its own speed.
                yield f"data: <span>{chunk}</span>\n\n"
                await asyncio.sleep(0.05)  # small delay for effect
            # Optional: send a closing event, but not strictly necessary for simple appending
            # unless we want to stop the client from reconnecting
        yield "event: close\ndata: \n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

