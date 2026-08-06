# Mxlit

Mxlit is a lightweight, pure-Python alternative to Streamlit, powered by **FastAPI** and **HTMX**. It allows you to build interactive web applications by writing simple top-to-bottom Python scripts, without having to write any HTML, CSS, or JavaScript.

## Features

- **No Frontend Code Required** — Write only Python; zero HTML, CSS, or JavaScript.
- **Fast and Lightweight** — HTMX partial-page reloads instead of heavy React bundles or WebSockets.
- **State Management** — Built-in `session_state` persists data across interactions, just like Streamlit.
- **Rich Components** — Text, markdown, dataframes, metrics, images, charts, and 11+ interactive widgets.
- **Layouts** — Sidebars, columns, tabs, expanders, and horizontal containers.
- **Advanced UI** — Named Entity Recognition (NER) highlighting and streaming text (`write_stream`) built in.
- **Python-Driven Styling** — Pass Tailwind utility classes to any component via `className="..."` directly from Python code.
- **Live Theme Generator** — `mt.theme(dict)` stores the palette in `session_state`; the framework injects CSS variables automatically on every response with no manual code needed.
- **oat.ink UI Library** — Semantic, zero-dependency component styles; buttons, alerts, tabs, and forms styled automatically.
- **Tailwind CSS v4** — Utility classes compiled to a single `style.css`; no Node.js required (uses `pytailwindcss`).

## Tech Stack

| Layer | Technology | Version | Role |
|-------|-----------|---------|------|
| Language | **Python** | 3.12+ | Application logic and component API |
| Web framework | **FastAPI** | 0.111+ | HTTP server, routing, SSE broadcast |
| ASGI server | **Uvicorn** | 0.29+ | Production-grade async server |
| Templating | **Jinja2** | 3.1+ | Server-side HTML rendering |
| Interactivity | **HTMX** | 2.x | Partial page reloads, SSE event handling |
| UI library | **oat.ink** | latest | Semantic, zero-dependency component styles (vendored) |
| CSS processor | **Tailwind CSS** | v4 | Utility-first CSS — no Node.js needed |
| CSS CLI | **pytailwindcss** | latest | pip-installable Tailwind v4 standalone binary |
| Charts | **Chart.js** | latest | Line, bar, area, and scatter charts |
| Data | **pandas** | 2.x | DataFrame and table rendering |

## Installation

### Option 1 — pip (recommended)

```bash
pip install mxlit
```

### Option 2 — from source using `setup.py`

Clone the repository and install in editable mode so any local changes are reflected immediately:

```bash
git clone https://github.com/kalpi-4/mxlit.git
cd mxlit
pip install -e .
```

Or install as a regular (non-editable) package from source:

```bash
pip install .
```

### Option 3 — with pinned dependencies (`requirements.txt`)

To reproduce the exact dependency versions used during development:

```bash
git clone https://github.com/kalpi-4/mxlit.git
cd mxlit
pip install -r requirements.txt
pip install -e .
```

### Option 4 — uv (fast, reproducible via `uv.lock`)

Clone the repository and let `uv` create the virtualenv and install everything
from the lockfile, including the `dev` extra (`pytailwindcss`, needed for the
automatic CSS rebuild on `mxlit run`):

```bash
git clone https://github.com/kalpi-4/mxlit.git
cd mxlit
uv sync --extra dev
```

> On a network with a TLS-intercepting proxy, add `--native-tls` (or set
> `UV_NATIVE_TLS=true`) if `uv sync` fails with a certificate error.

## Quick Start

Create a file named `app.py`:

```python
import mxlit as mt

mt.title("Hello Mxlit!")
mt.write("This is a simple interactive application.")

if "counter" not in mt.session_state:
    mt.session_state["counter"] = 0

if mt.button("Click me!"):
    mt.session_state["counter"] += 1

mt.write("Button clicked:", mt.session_state["counter"], "times")
```

Run your application using the Mxlit CLI:

```bash
mxlit run app.py
```

By default, the server will start at `http://127.0.0.1:8501`.

You can specify a custom host or port:

```bash
mxlit run app.py --host 0.0.0.0 --port 8000
```

If you installed with `uv` (Option 4), run through `uv run` instead so it
uses the project's managed virtualenv without activating it:

```bash
uv run mxlit run app.py
```

Try one of the bundled samples the same way:

```bash
uv run mxlit run .\samples\kitchen_sink.py
```

## How It Works

Mxlit executes your Python script top-to-bottom on every interaction. Behind the scenes:
1. The `mxlit` CLI spins up a FastAPI server.
2. The UI is dynamically generated as an HTML tree using Jinja2 templates.
3. User interactions (clicks, text input, slider changes) trigger HTMX `POST` requests to the server.
4. The server updates `session_state`, re-runs the Python script, and responds with only the HTML fragments that need to be updated.

## External API Interactions

Because Mxlit applications are powered by a standard FastAPI server, you can directly interact with the application's global state from external sources using simple HTTP POST requests.

### The `/interact` API
The `/interact` POST endpoint is typically used by the HTMX frontend to submit user interactions. However, you can call it manually (e.g., via webhooks or external scripts) by sending URL-encoded form data. The server updates the `session_state`, re-runs the Python script, and responds with the newly rendered HTML fragment.

### The `/modify` API (Real-time Broadcasts)
The `/modify` POST endpoint allows external systems or background workers to update the app's state and instantly push the updated UI to **all currently connected browsers** in real-time using Server-Sent Events (SSE). It returns a JSON status response, making it perfect for headless automation or IoT integrations.

```bash
curl -X POST http://127.0.0.1:8501/modify \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "counter=100"
```

## Advanced Usage

Mxlit supports many of the patterns you know and love:

```python
import mxlit as mt
import pandas as pd

# Layouts
with mt.sidebar:
    mt.header("Settings")
    rows = mt.slider("Rows to show", 1, 10, 5)

col1, col2 = mt.columns(2)
with col1:
    mt.metric("Users", 1024, "+12%")

# Dataframes
df = pd.DataFrame({"A": range(rows), "B": range(rows)})
mt.dataframe(df)

# Text Streaming
def my_stream():
    for word in ["Streaming ", "text ", "is ", "cool!"]:
        yield word
mt.write_stream(my_stream())
```

### Grid, rows, and columns

For finer control than `mt.columns()`, use OAT's 12-column grid directly —
`mt.grid()` holds one or more `mt.row()`s, each split into `mt.col()`s by
`span` (1-12), with optional `offset` and `end` alignment:

```python
import mxlit as mt

with mt.grid():
    with mt.row():
        with mt.col(6):
            mt.write("Left half")
        with mt.col(6):
            mt.write("Right half")

    with mt.row():
        with mt.col(4):
            mt.write("One third")
        with mt.col(4, offset=4):
            mt.write("Last third, shifted right")

    with mt.row():
        with mt.col(3, end=True):
            mt.metric("Uptime", "99.98%")
```

### Sidebar

`mt.sidebar` works as a bare context manager, a callable that accepts
`className`, or — matching OAT's `<aside data-sidebar>` recipe — as a context
manager yielding named `.header` / `.footer` slots, with any un-slotted
content falling into the middle `<nav>` region:

```python
import mxlit as mt

with mt.sidebar as s:
    with s.header:
        mt.write("Logo")
    mt.write("Nav link 1")   # un-slotted -> <nav>
    mt.write("Nav link 2")
    with s.footer:
        mt.button("Logout")

# or, styled and without slots:
with mt.sidebar(className="w-64"):
    mt.title("Nav")
```
---

### Customizing the theme

The theme is driven by `src/mxlit/constants/theme.json` — a [Material Theme Builder](https://m3.material.io/theme-builder) export. It contains 386 hex tokens organised by scheme and palette:

```json
{
  "schemes": {
    "light": {
      "primary":      "#415F91",
      "secondary":    "#565F71",
      "background":   "#F9F9FF",
      "onBackground": "#191C20"
    }
  },
  "palettes": {
    "primary": { "40": "#415F91", "80": "#AAC7FF" }
  }
}
```

Call `mt.theme()` to apply overrides at runtime. Keys are dot-notation paths into the JSON; CSS variables update automatically on the next response — no page reload needed.

```python
import mxlit as mt

# returns the full resolved dict (all 386 tokens)
_t = mt.theme()

# override any token
mt.theme({"schemes.light.primary": "#9333ea"})

# live color pickers — key follows "theme_" + path.replace(".", "_")
with mt.sidebar:
    mt.color_picker("Primary", value=_t["schemes.light.primary"],
                    key="theme_schemes_light_primary")
    mt.color_picker("Background", value=_t["schemes.light.background"],
                    key="theme_schemes_light_background")
```

See `samples/class_styling_demo.py` for a full working example.

---

### Passing utility classes from Python

Every mxlit component accepts an optional `className` keyword argument. The
value is a space-separated string of Tailwind utility classes applied
directly to the component's primary HTML element.

> **Full working demo** — `samples/class_styling_demo.py` showcases every
> component type with `className` applied, plus the live theme generator.
> Run it with `python -m mxlit run samples/class_styling_demo.py`.

```python
import mxlit as mt

# Typography — colour, size, weight
mt.title("Sales Dashboard",   className="text-3xl font-extrabold")
mt.write("Last updated: now", className="text-sm text-slate-400 italic")

# Badges — background and text colour via Tailwind
mt.badge("stable",     className="bg-green-100 text-green-800 font-semibold")
mt.badge("deprecated", className="bg-red-100   text-red-700   line-through")

# Full-width button
if mt.button("Save changes", className="w-full"):
    mt.success("Saved!", className="mt-1")

# Constrained form inputs
mt.text_input("Full name", className="max-w-sm")
mt.selectbox("Language", ["Python", "Rust", "Go"], className="max-w-xs")

# Chart with a card border
mt.bar_chart({"A": 10, "B": 20, "C": 15}, className="rounded-lg border p-2")

# Metric cards in a row
col1, col2 = mt.columns(2)
with col1: mt.metric("Revenue", "$84,200", "+12%", className="w-full")
with col2: mt.metric("Users",   "3,412",   "+5%",  className="w-full")

# Styled expander and pill container
with mt.expander("Model details", className="border rounded-lg"):
    mt.write("GPT-4o-mini · 128k context", className="text-sm")

with mt.container(horizontal=True, className="gap-3 flex-wrap p-4 bg-slate-50 rounded-xl border"):
    mt.badge("Python 3.12",  className="bg-blue-100  text-blue-800  text-sm px-3 py-1")
    mt.badge("Tailwind v4",  className="bg-sky-100   text-sky-800   text-sm px-3 py-1")
```

> **Note:** `error`/`warning`/`info`/`success` (in `status.py`) also accept a
> legacy `class_` kwarg as a compat alias for `className`. Every other
> component only accepts `className`.

**Where the class lands per component type**

| Component | Element that receives `className` |
|-----------|-------------------------------|
| `title` / `header` / `subheader` | `<h1>` / `<h2>` / `<h3>` |
| `write` / `text` | `<p>` |
| `markdown` / `html` | `<div>` |
| `code` / `json` | `<pre>` |
| `latex` | `<div class="mx-latex …">` |
| `badge` | `<span class="badge …">` |
| `error` / `warning` / `info` / `success` | `<div role="alert" …>` |
| `button` | `<button>` |
| `text_input` / `checkbox` / `slider` / `toggle` / `number_input` / `text_area` / `date_input` / `color_picker` | `<label>` wrapper |
| `radio` | `<fieldset>` |
| `selectbox` | `<div data-field>` wrapper |
| `dataframe` / `table` | `<div class="table …">` |
| `metric` | `<div class="mx-metric …">` |
| `image` / `logo` | `<img>` |
| `audio` | `<audio>` |
| `video` | `<video>` |
| `line_chart` / `bar_chart` / `area_chart` / `scatter_chart` | `<div class="mx-chart …">` |
| `expander` | `<details>` |
| `container` | `<div>` |
| `ner_text` | outer `<div class="mx-ner …">` |
| `write_stream` | `<div class="mx-stream …">` |