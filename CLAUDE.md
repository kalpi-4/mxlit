# mxlit — Claude Project Guide

> A Streamlit alternative powered by **FastAPI · Uvicorn · HTMX · Jinja2 · Python 3.10+**  
> Single-process, stateful server with Server-Sent Events (SSE).
>
> **PLAN.md status: fully implemented.** All architecture, component factory pattern,
> targeted updates, auto-refresh, and OAT component catalog are live in the codebase.

---

## 0. Development Quick Start

```bash
# Install (editable) with dev tools
pip install -e ".[dev]"

# Run a sample app
mxlit run samples/demo_app.py

# Rebuild Tailwind CSS (only needed after editing input.css)
python -m pytailwindcss -i src/mxlit/static/input.css \
                        -o src/mxlit/static/style.css
```

---

## 1. Project Structure

```
mxlit/                              ← repository root
├── CLAUDE.md                       ← this file (Claude project guide)
├── docs/
│   ├── PLAN.md                     ← component architecture plan (FULLY IMPLEMENTED)
│   ├── DRY_VIOLATION.md            ← 43-instance boilerplate tracker (resolved)
│   ├── functionalities.md          ← Streamlit API reference
│   └── TODO.md                     ← implementation coverage tracker + complexity tiers
├── samples/                        ← example user apps
│   ├── class_styling_demo.py       ← Material token showcase + live theme generator
│   ├── oar_demo.py                 ← full dashboard demo (oat.ink)
│   ├── oat_sample.py               ← oat.ink component playground
│   ├── kitchen_sink.py             ← every component in one file (primary reference)
│   ├── demo_app.py
│   ├── demo_new_features.py        ← all new widgets / OAT primitives showcase
│   ├── live_feed_demo.py           ← setInterval / setTimeout demo
│   └── cgpa_calc.py
├── src/
│   └── mxlit/                      ← installable package
│       ├── __init__.py             ← public API surface
│       ├── _exceptions.py          ← RerunException(BaseException)
│       ├── _paths.py               ← PACKAGE_DIR, STATIC_DIR, TEMPLATES_DIR, INPUT_CSS, OUTPUT_CSS
│       ├── cli.py                  ← `mxlit run` entry point
│       ├── server.py               ← FastAPI app (routes, SSE, state, /refresh/{id})
│       ├── context.py              ← per-request AppContext (+ _auto_refresh field)
│       ├── state.py                ← SessionState (global, in-memory)
│       ├── timers.py               ← setInterval(sync_time), setTimeout(delay) context managers
│       ├── components/
│       │   ├── base.py             ← ComponentType, HtmxProps, OatProps, BaseComponent,
│       │   │                           CompositeComponent, @component, @widget_component,
│       │   │                           reset_render_counts()
│       │   ├── charts.py           ← line/bar/area/scatter charts
│       │   ├── data.py             ← dataframe, table, json, metric
│       │   ├── layout.py           ← sidebar, columns, tabs, expander, container, card,
│       │   │                           spinner, progress, skeleton, meter, avatar,
│       │   │                           avatar_group, breadcrumb, button_group, toast,
│       │   │                           dialog, dropdown, grid, input_group, space, empty,
│       │   │                           popover, status, page_config
│       │   ├── media.py            ← image, audio, video, logo
│       │   ├── status.py           ← error, warning, info, success, exception
│       │   ├── text.py             ← write, markdown, title, latex, badge, ner_text …
│       │   ├── theme.py            ← mt.theme() — live theme API
│       │   └── widgets.py          ← button, slider, selectbox, email_input,
│       │                               password_input, datetime_input, file_input,
│       │                               pagination, multiselect, select_slider,
│       │                               time_input, link_button, download_button,
│       │                               pills, feedback …
│       ├── constants/
│       │   ├── __init__.py         ← re-exports THEME_KEY, _DEFAULTS, _FLAT_KEYS
│       │   ├── theme.json          ← 386-token Material Theme Builder palette
│       │   └── theme.py            ← _flatten_theme(), _DEFAULTS, _FLAT_KEYS
│       ├── static/
│       │   ├── htmx.min.js         ← HTMX library (vendored)
│       │   ├── sse.js              ← HTMX SSE extension (vendored)
│       │   ├── oat.min.css         ← oat.ink component library CSS (vendored)
│       │   ├── oat.min.js          ← oat.ink component library JS (vendored)
│       │   ├── input.css           ← Tailwind source (edit here, then rebuild)
│       │   └── style.css           ← compiled Tailwind output
│       └── templates/
│           ├── base.html           ← app shell (HTMX, oat.ink, Chart.js, SSE)
│           ├── components.html     ← Jinja2 macro component renderer
│           └── component_fragment.html ← single-component fragment for targeted outerHTML swaps
├── pyproject.toml                  ← build config (hatchling)
├── uv.lock                         ← locked dependency graph
└── README.md
```

---

## 2. Architecture

### 2.1 How mxlit Works

User scripts call `mxlit.*` functions which push component descriptors into an
`AppContext`. On every HTMX POST to `/interact`, the script is re-run top-to-bottom
and `components.html` renders the new component tree as HTML fragments.

### 2.2 Single-Instance Topology (MVP / hobby)

```
                        ┌─────────────────────────────┐
   Browser              │     Cloud Instance (1×)      │
  ──────────            │                              │
  GET  /         ──────►│  Uvicorn (ASGI)              │
  POST /interact ──────►│    └─ FastAPI app            │
  GET  /events   ──────►│         ├─ SessionState (RAM)│
  GET  /stream/* ──────►│         └─ SSE queues (RAM)  │
                        │                              │
                        │  mxlit run samples/app.py    │
                        └─────────────────────────────┘
```

**Suitable platforms:** Fly.io (single machine), Railway, Render, AWS App Runner

---

### 2.3 Multi-Instance Topology (production / scale-out)

```
          ┌──────────────────────────────────────────────────┐
          │                Load Balancer                     │
          │        (sticky sessions via cookie/header)       │
          └────────┬─────────────────────────┬──────────────┘
                   │                         │
        ┌──────────▼──────────┐   ┌──────────▼──────────┐
        │  mxlit instance A   │   │  mxlit instance B   │
        │  Uvicorn / FastAPI  │   │  Uvicorn / FastAPI  │
        └──────────┬──────────┘   └──────────┬──────────┘
                   │                         │
          ┌────────▼─────────────────────────▼────────┐
          │               Redis                        │
          │  ┌─────────────────┐  ┌─────────────────┐ │
          │  │  Session State  │  │  Pub/Sub (SSE)  │ │
          │  │  (HASH per sid) │  │  channel/sid    │ │
          │  └─────────────────┘  └─────────────────┘ │
          └───────────────────────────────────────────┘
```

**Key changes required for scale-out:**
- Replace `state.SessionState` (in-memory dict) with a Redis-backed session store
- Replace in-process `sse_clients` set with Redis Pub/Sub channels
- Add session-id cookie on first `GET /` and thread it through all requests
- Configure the load balancer for **sticky sessions** as a short-term fallback

---

## 3. Containerisation

### 3.1 Dockerfile

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir hatchling
COPY pyproject.toml uv.lock ./
COPY src/ src/
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels mxlit \
    && rm -rf /wheels
COPY samples/ samples/
EXPOSE 8501
ENV MXLIT_SCRIPT=/app/samples/demo_app.py HOST=0.0.0.0 PORT=8501
CMD ["sh", "-c", "mxlit run $MXLIT_SCRIPT --host $HOST --port $PORT"]
```

---

## 4. Platform Deployment Configs

See `CLAUDE.md` sections 4.1–4.3 for Fly.io, Railway, and AWS App Runner configs.
Key point: SSE requires persistent TCP — avoid platforms with forced HTTP/1.1 timeouts.

---

## 5. Persistent Session State & SSE (Distributed)

See §2.3 for Redis topology. Drop-in `SessionState` and SSE Pub/Sub replacements
are documented inline in the project README.

---

## 6. Theme System — `mt.theme()` and Material Design Tokens

### 6.1 How It Works

`mt.theme()` reads `session_state[THEME_KEY]`, merges any overrides, persists the result,
and returns the full resolved token dict:

```python
_t = mt.theme()                              # read current palette
_t = mt.theme({"schemes.light.primary": "#9333ea"})  # override + read
primary_hex = _t["schemes.light.primary"]
```

The Jinja2 template emits the resolved palette as CSS variables on every HTMX response.

### 6.2 Token Keys

Keys are **dot-notation paths** into `constants/theme.json`:

| Token key | CSS variable |
|---|---|
| `schemes.light.primary` | `--primary` |
| `schemes.light.secondary` | `--secondary` |
| `schemes.light.background` | `--background` / `--card` |
| `schemes.light.onBackground` | `--foreground` / `--card-foreground` |

### 6.3 Color-Picker Widget Absorption

`color_picker` widgets write back using the flat-key alias:
```
"theme_" + token_key.replace(".", "_")
```
Example: `key="theme_schemes_light_primary"` → absorbed by `mt.theme()` on next re-run.

### 6.4 Preset Pattern

```python
_PRESETS = {
    "btn_ocean": {"schemes.light.primary": "#57575C", "schemes.light.secondary": "#33A05A"},
}
for _pk, _pv in _PRESETS.items():
    if mt.session_state.get(_pk) == "true":
        _t = mt.theme(_pv)
        mt.session_state[_pk] = "false"
        break
else:
    _t = mt.theme()
```

---

## 7. OAT Integration — oat.ink UI Patterns

### 7.1 Styling Philosophy

oat.ink styles through **semantic HTML attributes**, not utility classes:

| ✅ Correct (OAT) | ❌ Wrong (hardcoded Tailwind) |
|---|---|
| `data-variant="error"` | `className="bg-red-100 text-red-700"` |
| `data-field` wrapper | `className="border rounded px-2"` |
| `role="switch"` | `className="toggle-switch"` |
| `aria-busy="true"` | `className="loading"` |

Use `className=` only for **layout** (`w-full`, `mt-4`, `rounded-lg`) and **typography**
adjustments (`text-xs`, `font-bold`). Never use Tailwind colour classes for semantic
meaning — use OAT variant attributes instead.

### 7.2 Key OAT Attributes

| HTML attribute | Values | Rendered by |
|---|---|---|
| `data-variant` | `success` `warning` `error` `danger` `secondary` | alert, badge, button, avatar |
| `data-field` | `""` (standard) `"error"` (red border) | all form field wrappers |
| `role="alert"` | — | `error`, `warning`, `info`, `success` banners |
| `role="switch"` | — | `toggle` component |
| `aria-busy="true"` | — | spinner / loading overlay |
| `data-spinner` | `small` `large` `overlay` | spinner size modifier |
| `title="…"` | tooltip text | any element — OAT renders smooth tooltip |

### 7.3 Component → OAT Mapping

| mxlit function | OAT element |
|---|---|
| `mt.error/warning/info/success` | `<div role="alert" data-variant="…">` |
| `mt.button` | `<button data-variant="secondary">` |
| `mt.toggle` | `<input type="checkbox" role="switch">` |
| `mt.text_input` / etc. | `<input>` inside `<label data-field>` |
| `mt.tabs` | `<ot-tabs>` WebComponent |
| `mt.sidebar` | `<aside data-sidebar>` in `[data-sidebar-layout]` |
| `mt.expander` | `<details><summary>` |
| `mt.badge` | `<span class="badge" data-variant="…">` |
| `mt.card` | `<article class="card">` |
| `mt.spinner` | `<div aria-busy="true" data-spinner="…">` |
| `mt.progress` | Native `<progress value max>` |
| `mt.skeleton` | `<div role="status" class="skeleton line\|box">` |
| `mt.meter` | Native `<meter>` |
| `mt.avatar` | `<figure data-variant="avatar">` |
| `mt.dropdown` | `<ot-dropdown>` WebComponent |

---

## 8. Component Architecture (`src/mxlit/components/base.py`)

### 8.1 Current Pattern (use this for ALL new components)

All components use `@component` / `@widget_component` from `base.py`. Raw boilerplate is retired.

**Display component** (no return value):

```python
from mxlit.components.base import component, ComponentType

@component(ComponentType.MY_COMPONENT)
def my_component(label: str) -> tuple:
    props = {"label": label}
    fallback = lambda: print(f"[MY_COMPONENT] {label}")
    return props, fallback
```

**Widget** (returns a value from `session_state`):

```python
from mxlit.components.base import widget_component, ComponentType, BaseComponent
from mxlit.state import session_state

@widget_component(ComponentType.MY_WIDGET)
def my_widget(label: str, value: str = "", key: str = None) -> tuple:
    widget_key = key or BaseComponent.generate_key(ComponentType.MY_WIDGET, label)
    current = session_state.get(widget_key, value)
    props = {"label": label, "value": current, "key": widget_key}
    return props, current
```

**Decorator kwargs:** `id=`, `className=` only. `class_` is NOT accepted — use `className=` exclusively.

### 8.2 `base.py` Type Reference

| Class / Function | Purpose |
|---|---|
| `ComponentType(str, Enum)` | Exhaustive typed registry of all component type strings |
| `HtmxProps` dataclass | Strongly-typed container for every `hx-*` attribute; `.to_attrs()` → dict |
| `OatProps` dataclass | OAT semantic attrs (`data-variant`, `role`, `data-field`, `aria-busy`, …); `.to_attrs()` → dict |
| `BaseComponent` dataclass | Root: constructs, registers in `__post_init__` via `ctx.add_component(self.to_dict())` |
| `CompositeComponent(BaseComponent)` | Deferred registration via `with` block; nests children in `d["children"]` |
| `@component(type, *, htmx, oat)` | Turns a props-builder into a registered display component |
| `@widget_component(type, *, htmx, oat)` | Turns a props-builder into a stateful widget (return value preserved) |
| `reset_render_counts()` | Clears per-type render-order counters; called before each script execution |
| `BaseComponent.generate_key(type, discriminator)` | Stable MD5-based widget key |

### 8.3 `HtmxProps` — Quick Reference

`HtmxProps` is passed to `@component` / `@widget_component` via the `htmx=` kwarg.
`to_attrs()` emits only non-None/non-False fields.

| Python field | HTML attribute | Default | Type |
|---|---|---|---|
| `post` | `hx-post` | `"/interact"` | `str \| None` |
| `get` | `hx-get` | `None` | `str \| None` |
| `put` / `patch` / `delete` | `hx-put` etc. | `None` | `str \| None` |
| `target` | `hx-target` | `"#app-root"` | `str \| None` |
| `swap` | `hx-swap` | `"innerHTML settle:0"` | `str \| None` |
| `swap_oob` | `hx-swap-oob` | `None` | `str \| None` |
| `select` / `select_oob` | `hx-select` etc. | `None` | `str \| None` |
| `trigger` | `hx-trigger` | `"change"` | `str \| None` |
| `boost` / `validate` | `hx-boost` etc. | `False` | `bool` → bare attr |
| `vals` | `hx-vals` | `None` | `dict \| str \| None` → JSON |
| `headers` | `hx-headers` | `None` | `dict \| str \| None` → JSON |
| `include` | `hx-include` | `None` | `str \| None` |
| `params` | `hx-params` | `None` | `"*" \| "none" \| CSV` |
| `encoding` | `hx-encoding` | `None` | `"multipart/form-data" \| …` |
| `sync` | `hx-sync` | `None` | `"{selector}:{strategy}"` |
| `disabled_elt` | `hx-disabled-elt` | `None` | `str \| None` |
| `indicator` | `hx-indicator` | `None` | CSS selector |
| `confirm` | `hx-confirm` | `None` | dialog text |
| `push_url` / `replace_url` | `hx-push-url` etc. | `None` | `str \| bool \| None` |
| `history` | `hx-history` | `None` | `"false" \| None` |
| `disable` / `disinherit` / `inherit` / `preserve` | inheritance control | `False / None` | `bool / str` |

**Widget default preset** (all four mxlit defaults):
```python
_HTMX_CHANGE = HtmxProps(
    post    = "/interact",
    target  = "#mx-{comp.id}",   # targeted self-update
    swap    = "outerHTML settle:100ms",
    trigger = "change",
    include = "[name]",
)
```

**File upload:**
```python
HtmxProps(encoding="multipart/form-data", trigger="change", include="[name]")
```

### 8.4 `OatProps` — Quick Reference

| Python field | HTML attribute | Example value |
|---|---|---|
| `variant` | `data-variant` | `"success"`, `"error"`, `"danger"`, `"warning"`, `"secondary"` |
| `role` | `role` | `"alert"`, `"switch"`, `"status"` |
| `field` | `data-field` | `True` → `""`, `"error"` → `data-field="error"` |
| `busy` | `aria-busy` | `True` → `"true"` |
| `spinner` | `data-spinner` | `"small"`, `"large"`, `"overlay"` |
| `tooltip` | `title` | any tooltip string |

Usage:
```python
@component(ComponentType.SUCCESS, oat=OatProps(role="alert", variant="success"))
def success(message: str) -> tuple:
    return ({"content": message}, None)
```

### 8.5 Targeted Update Strategy (implemented)

Every widget interaction targets only its own wrapper — not `#app-root`.

- Every rendered component is wrapped in `<div id="mx-{{ comp.id }}">` in `components.html`
- Widgets use `hx-target="#mx-{{ comp.id }}"` + `hx-swap="outerHTML settle:100ms"` + `hx-include="[name]"`
- Buttons use `type="button"` + `hx-target="#app-root"` (full re-render)
- `#app-root` div uses `hx-trigger="load"` for initial render only
- `component_fragment.html` handles single-component fragment responses for targeted swaps
- Auto-refresh wrappers emit HTMX poll attributes when `comp.refresh_trigger` is set

### 8.6 `className` — the only CSS class parameter

`className=` is the **only** accepted kwarg for CSS classes on all components.
`class_=` is not accepted anywhere (no alias, no fallback).

- **Decorator-wrapped components:** pass `className="..."` as kwarg to the call site
- **Layout CompositeComponents** (`columns`, `tabs`, `expander`, `container`, etc.): pass `className="..."` as named param
- **Template:** reads `comp.className` (not `comp.class_`)
- **Internal layout props:** `columnsClassName` (wrapper div class from `columns()`), `tabsClassName` (wrapper class from `tabs()`)

```python
# Correct
mt.button("Save", className="w-full")
mt.columns(2, className="gap-4")
with mt.expander("Details", className="border rounded-lg"):
    mt.write("content")

# Wrong — will be silently ignored or raise TypeError
mt.button("Save", class_="w-full")   # ❌
```

### 8.7 Auto-Refresh — `mt.setInterval` / `mt.setTimeout`

```python
import mxlit as mt

# Refresh components in this block every 10 seconds
with mt.setInterval(sync_time=10):
    mt.scatter_chart(data, id="live_chart")

# Re-fetch once after 5 seconds
with mt.setTimeout(delay=5):
    mt.info("Checking status…", id="status_msg")
```

Both are context managers from `src/mxlit/timers.py`. They set `ctx._auto_refresh` on
the active `AppContext`; `components.html` emits the HTMX poll trigger on each wrapped component.

### 8.8 Utility APIs

```python
mt.stop()                     # sys.exit(0) — halt script execution
mt.rerun()                    # raise RerunException — immediately re-run script

@mt.cache_data                # lru_cache for data-producing functions
def load_df(path): ...

@mt.cache_resource            # lru_cache for singleton objects (models, connections)
def load_model(): ...

mt.get_option("client.showErrorDetails")  # read a mxlit option
mt.set_option("server.maxUploadSize", 50) # set a mxlit option
```

### 8.9 Atomic Composition Factories

Several component families are generated from a single factory rather than defined individually:

**Status variants** (`status.py`):
```python
def _make_status_variant(status_type: str) -> Callable:
    oat = OatProps(role="alert", variant=status_type if status_type != "info" else None)
    @component(ComponentType.STATUS, oat=oat)
    def _fn(message: str) -> tuple:
        return ({"content": message, "status_type": status_type}, None)
    return _fn

error   = _make_status_variant("error")
warning = _make_status_variant("warning")
info    = _make_status_variant("info")
success = _make_status_variant("success")
```

**Heading levels** (`text.py`):
```python
title    = _make_heading(ComponentType.TITLE,    "TITLE")
header   = _make_heading(ComponentType.HEADER,   "HEADER")
subheader= _make_heading(ComponentType.SUBHEADER,"SUBHEADER")
```

**Charts** (`charts.py`):
```python
line_chart    = _make_chart(ComponentType.LINE_CHART,    "line")
bar_chart     = _make_chart(ComponentType.BAR_CHART,     "bar")
area_chart    = _make_chart(ComponentType.AREA_CHART,    "line")  # fill=true
scatter_chart = _make_chart(ComponentType.SCATTER_CHART, "scatter")
```

---

## 9. Component Inventory

All components from the original gap analysis are implemented. Full public API:

### 9.1 Layout & Containers

| Function | OAT / HTML element | Notes |
|---|---|---|
| `mt.sidebar()` | `<aside data-sidebar>` | `with` block; `className=` for extra classes |
| `mt.columns(n)` | flex column slots | `with` block; `className=` on wrapper div |
| `mt.tabs(labels)` | `<ot-tabs>` WebComponent | `with` block; `className=` on ot-tabs |
| `mt.expander(label)` | `<details><summary>` | `with` block |
| `mt.container()` | `<div>` wrapper | `with` block |
| `mt.card(header, footer)` | `<article class="card">` | `with` block — CompositeComponent |
| `mt.dialog(title, trigger_label)` | `<dialog closedby="any">` | `with` block — CompositeComponent |
| `mt.avatar_group(size)` | `<figure>` grouping | `with` block — CompositeComponent |
| `mt.grid()` | `<div class="container"><div class="row">` | `with` block |
| `mt.input_group(prefix, suffix)` | `<fieldset class="group">` | `with` block |

### 9.2 OAT UI Primitives

| Function | OAT / HTML element |
|---|---|
| `mt.spinner(size)` | `<div aria-busy="true" data-spinner="…">` |
| `mt.progress(value, max)` | Native `<progress value max>` |
| `mt.skeleton(variant)` | `<div role="status" class="skeleton line\|box">` |
| `mt.meter(value, min, max, low, high, optimum)` | Native `<meter>` |
| `mt.avatar(src, initials, size)` | `<figure data-variant="avatar">` |
| `mt.breadcrumb(items)` | `<nav aria-label="Breadcrumb"><ol class="unstyled hstack">` |
| `mt.button_group(labels)` | `<menu class="buttons">` |
| `mt.toast(message, variant)` | `ot.toast()` JS call via SSE |
| `mt.dropdown(label)` | `<ot-dropdown>` WebComponent |
| `mt.space()` / `mt.empty()` | Spacer / structural placeholder |
| `mt.popover()` | HTML Popover API wrapper |
| `mt.status()` | Expandable status container (running/complete/error) |

### 9.3 Widgets (return values from `session_state`)

| Function | Input type | Notes |
|---|---|---|
| `mt.button(label)` | click → bool | `type="button"`, full re-render |
| `mt.text_input(label, value, key)` | `type="text"` | |
| `mt.email_input(label, value, key)` | `type="email"` | browser validation |
| `mt.password_input(label, key)` | `type="password"` | never stored in session |
| `mt.datetime_input(label, value, key)` | `type="datetime-local"` | |
| `mt.date_input(label, value, key)` | `type="date"` | |
| `mt.time_input(label, value, key)` | `type="time"` | |
| `mt.number_input(label, value, key)` | `type="number"` | |
| `mt.text_area(label, value, key)` | `<textarea>` | |
| `mt.checkbox(label, value, key)` | `type="checkbox"` | |
| `mt.toggle(label, value, key)` | `role="switch"` | |
| `mt.radio(label, options, key)` | radio group | |
| `mt.selectbox(label, options, key)` | `<select>` | |
| `mt.multiselect(label, options, key)` | multi-select | |
| `mt.select_slider(label, options, key)` | slider over discrete options | |
| `mt.slider(label, min, max, key)` | `type="range"` | |
| `mt.color_picker(label, value, key)` | `type="color"` | integrates with theme system |
| `mt.file_input(label, accept, key)` | `type="file"` | multipart encoding |
| `mt.pagination(total, current, key)` | page nav | returns current page number |
| `mt.pills(options, key)` | pill selector | |
| `mt.feedback(key)` | star/emoji feedback | |
| `mt.link_button(label, url)` | `<a>` styled as button | |
| `mt.download_button(label, data, key)` | download trigger | |

---

## 10. Deployment Configs

### 10.1 Fly.io (`fly.toml`)

```toml
app = "mxlit-app"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8501"
  HOST = "0.0.0.0"

[http_service]
  internal_port        = 8501
  force_https          = true
  auto_stop_machines   = true
  auto_start_machines  = true
  min_machines_running = 1

  [http_service.concurrency]
    type       = "connections"
    hard_limit = 500
    soft_limit = 400

[[vm]]
  memory = "512mb"
  cpus   = 1
```

```bash
fly secrets set MXLIT_SCRIPT=/app/samples/demo_app.py
fly deploy
```

### 10.2 Railway (`railway.toml`)

```toml
[build]
  builder        = "dockerfile"
  dockerfilePath = "Dockerfile"

[deploy]
  startCommand            = "mxlit run $MXLIT_SCRIPT --host 0.0.0.0 --port $PORT"
  healthcheckPath         = "/"
  healthcheckTimeout      = 30
  restartPolicyType       = "on_failure"
  restartPolicyMaxRetries = 3
```

### 10.3 AWS App Runner (`apprunner.yaml`)

```yaml
version: 1.0
runtime: python311
build:
  commands:
    build:
      - pip install hatchling
      - pip install .
run:
  command: mxlit run $MXLIT_SCRIPT --host 0.0.0.0 --port 8080
  network:
    port: 8080
```

> **App Runner SSE caveat:** Send `": heartbeat\n\n"` every 60 s from `event_generator`
> to keep connections alive past the 120 s idle timeout.

---

## 11. Deployment Checklist

### Before deploying
- [ ] Set `MXLIT_SCRIPT` environment variable / secret
- [ ] Set `REDIS_URL` secret if using multi-instance deployment
- [ ] Confirm `HOST=0.0.0.0` (not `127.0.0.1`) inside container
- [ ] Vendor or pin `htmx.min.js` and `sse.js` (already in `static/`)

### Single-instance (MVP)
- [ ] Build Docker image and verify locally
- [ ] Push to chosen platform (Fly / Railway / App Runner)
- [ ] Smoke-test `/`, `/interact`, `/events` endpoints
- [ ] Verify SSE by opening two browser tabs and triggering `/modify`

### Multi-instance (production)
- [ ] Provision Redis (Fly Redis / Railway Redis plugin / AWS ElastiCache)
- [ ] Swap `state.py` for Redis-backed `SessionState`
- [ ] Swap `sse_clients` set for Redis Pub/Sub in `server.py`
- [ ] Add session-id cookie issuance on `GET /`
- [ ] Configure sticky sessions or verify Redis fanout covers all instances
- [ ] Set load-balancer idle timeout ≥ 300 s
- [ ] Add SSE heartbeat (`": heartbeat\n\n"` every 60 s)
- [ ] Enable health-check route (`GET /` returns 200)
- [ ] Set `min_machines_running = 1` to prevent scale-to-zero

---

## 12. Adding New Components — Checklist

1. **Add `ComponentType` entry** in `base.py` enum
2. **Write component function** in the appropriate file using `@component` or `@widget_component`
3. **Add template branch** in `components.html` `render_component` macro
4. **Export** from `__init__.py`
5. **Add sample usage** in `samples/kitchen_sink.py` or `samples/demo_new_features.py`
6. **Update** `docs/TODO.md` status

**Decision tree:**
- Returns a value from session_state? → `@widget_component` + `HtmxProps` for HTMX attrs
- Display only? → `@component`
- Needs children (context manager)? → `CompositeComponent` directly (see `layout.py` pattern)
- Family of variants sharing same shape? → atomic factory function (see `status.py`, `text.py`, `charts.py`)

---

## 13. Known Partial Implementations

| Item | Status | Fix needed |
|---|---|---|
| `st.bar_chart(horizontal=True)` | `[~]` | Wire `indexAxis: 'y'` in Chart.js config in `components.html:~370` |
| `st.columns(vertical_alignment=)` | `[~]` | Apply `align-items` CSS to flex wrapper using `comp.vertical_alignment` |
| `st.set_page_config()` | `[~]` | Extend `page_config()` with `page_title`, `page_icon`, `layout` params injected into `base.html` |
| `st.file_uploader()` | `[~]` | Browser-side only; no server-side file object yet |

See `docs/TODO.md` for full complexity-tiered list of unimplemented items.
