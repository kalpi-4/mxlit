# Mxlit

Mxlit is a lightweight, pure-Python alternative to Streamlit, powered by **FastAPI** and **HTMX**. It allows you to build interactive web applications by writing simple top-to-bottom Python scripts, without having to write any HTML, CSS, or JavaScript.

## Features

- **No Frontend Code Required** — Write only Python; zero HTML, CSS, or JavaScript.
- **Fast and Lightweight** — HTMX partial-page reloads instead of heavy React bundles or WebSockets.
- **State Management** — Built-in `session_state` persists data across interactions, just like Streamlit.
- **Rich Components** — Text, markdown, dataframes, metrics, images, charts, and 11+ interactive widgets.
- **Layouts** — Sidebars, columns, tabs, expanders, and horizontal containers.
- **Advanced UI** — Named Entity Recognition (NER) highlighting and streaming text (`write_stream`) built in.
- **Python-Driven Styling** — Pass Tailwind utility classes to any component via `class_="..."` directly from Python code.
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

Every mxlit component accepts an optional `class_` keyword argument (the trailing
underscore avoids a clash with Python's `class` keyword). The value is a
space-separated string of Tailwind utility classes applied directly to the
component's primary HTML element.

> **Full working demo** — `samples/class_styling_demo.py` showcases every
> component type with `class_` applied, plus the live theme generator.
> Run it with `python -m mxlit run samples/class_styling_demo.py`.

```python
import mxlit as mt

# Typography — colour, size, weight
mt.title("Sales Dashboard",   class_="text-3xl font-extrabold")
mt.write("Last updated: now", class_="text-sm text-slate-400 italic")

# Badges — background and text colour via Tailwind
mt.badge("stable",     class_="bg-green-100 text-green-800 font-semibold")
mt.badge("deprecated", class_="bg-red-100   text-red-700   line-through")

# Full-width button
if mt.button("Save changes", class_="w-full"):
    mt.success("Saved!", class_="mt-1")

# Constrained form inputs
mt.text_input("Full name", class_="max-w-sm")
mt.selectbox("Language", ["Python", "Rust", "Go"], class_="max-w-xs")

# Chart with a card border
mt.bar_chart({"A": 10, "B": 20, "C": 15}, class_="rounded-lg border p-2")

# Metric cards in a row
col1, col2 = mt.columns(2)
with col1: mt.metric("Revenue", "$84,200", "+12%", class_="w-full")
with col2: mt.metric("Users",   "3,412",   "+5%",  class_="w-full")

# Styled expander and pill container
with mt.expander("Model details", class_="border rounded-lg"):
    mt.write("GPT-4o-mini · 128k context", class_="text-sm")

with mt.container(horizontal=True, class_="gap-3 flex-wrap p-4 bg-slate-50 rounded-xl border"):
    mt.badge("Python 3.12",  class_="bg-blue-100  text-blue-800  text-sm px-3 py-1")
    mt.badge("Tailwind v4",  class_="bg-sky-100   text-sky-800   text-sm px-3 py-1")
```

**Where the class lands per component type**

| Component | Element that receives `class_` |
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