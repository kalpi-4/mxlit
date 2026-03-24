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

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
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
    path = os.environ.get("ALTLIT_SCRIPT")
    if not path or not Path(path).is_file():
        raise RuntimeError("ALTLIT_SCRIPT environment variable not set or file not found.")
    return path

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the initial app shell."""
    return templates.TemplateResponse("base.html", {"request": request})

@app.post("/interact", response_class=HTMLResponse)
async def interact(request: Request):
    """
    Handle HTMX interactions.
    Re-runs the script and returns the updated components HTML.
    """
    form_data = await request.form()
    
    # We need to know all known checkbox keys to handle unchecked state
    # A robust way is to track registered widgets from the previous run, 
    # but for simplicity, we'll prefix widget names in the HTML or infer from context.
    # Alternatively, use a hidden input for checkboxes in HTML.
    
    for key, value in form_data.items():
        # Try to cast value to existing type if it exists in session_state
        if key in session_state:
            old_value = session_state[key]
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
                # Handle boolean casting, usually form values are strings like "true" or "false"
                if str(value).lower() in ("true", "1", "yes", "on"):
                    value = True
                elif str(value).lower() in ("false", "0", "no", "off"):
                    value = False

        session_state[key] = value
        
    # Checkbox logic: unchecked checkboxes do not send form data.
    # We can handle this by adding a hidden input with the same name before the checkbox, 
    # and parsing the list of values (if "true" is present, it's checked, otherwise false).
    # Since FastAPI Request.form() returns the last value by default, this trick works well:
    # <input type="hidden" name="key" value="false">
    # <input type="checkbox" name="key" value="true">
    
    script_path = get_script_path()
    
    ctx = AppContext()
    token = _current_context.set(ctx)
    try:
        # Re-run the user script top-to-bottom
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        if type(e).__name__ == "RerunException":
            # If the user script called `at.rerun()`, that's fine, we just stop executing and render.
            # In a real implementation we might re-run again, but for this demo, stopping and rendering is ok.
            pass
        else:
            ctx.add_component({"type": "write", "args": (f"Error executing script: {e}",)})
    finally:
        _current_context.reset(token)
        
    return templates.TemplateResponse(
        "components.html", 
        {"request": request, "components": ctx.components}
    )

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
                    yield f"{formatted_data}\n\n"
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
    Modify state and push update to all connected clients.
    """
    form_data = await request.form()
    for key, value in form_data.items():
        # Try to cast value to existing type if it exists in session_state
        if key in session_state:
            old_value = session_state[key]
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
                # Handle boolean casting, usually form values are strings like "true" or "false"
                if str(value).lower() in ("true", "1", "yes", "on"):
                    value = True
                elif str(value).lower() in ("false", "0", "no", "off"):
                    value = False

        session_state[key] = value

    script_path = get_script_path()
    
    ctx = AppContext()
    token = _current_context.set(ctx)
    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        if type(e).__name__ == "RerunException":
            pass
        else:
            ctx.add_component({"type": "write", "args": (f"Error executing script: {e}",)})
    finally:
        _current_context.reset(token)

    html_content = templates.get_template("components.html").render(
        {"request": request, "components": ctx.components}
    )

    for queue in sse_clients:
        queue.put_nowait(html_content)
        
    return JSONResponse(content={"status": "success", "message": "State updated and broadcasted"})

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

