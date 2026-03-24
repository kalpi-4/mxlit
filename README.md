# Mxlit

Mxlit is a lightweight, pure-Python alternative to Streamlit, powered by **FastAPI** and **HTMX**. It allows you to build interactive web applications by writing simple top-to-bottom Python scripts, without having to write any HTML, CSS, or JavaScript.

## Features

- **No Frontend Code Required**: Write only Python.
- **Fast and Lightweight**: Uses HTMX for seamless partial page reloads instead of heavy React bundles and Websockets.
- **State Management**: Built-in `session_state` to persist data across interactions.
- **Rich Components**: Support for text, markdown, dataframes, metrics, images, and interactive widgets (buttons, text inputs, sliders, checkboxes).
- **Layouts**: Organize your app using sidebars, columns, tabs, and expanders.
- **Advanced UI**: Includes Named Entity Recognition (NER) highlighting and streaming text out of the box.

## Installation

Install Mxlit via pip:

```bash
pip install mxlit
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
