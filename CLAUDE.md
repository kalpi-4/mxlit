# mxlit — Claude Project Guide

> A Streamlit alternative powered by **FastAPI · Uvicorn · HTMX · Jinja2 · Python 3.10+**  
> Single-process, stateful server with Server-Sent Events (SSE).

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
│   ├── PLAN.md                     ← component architecture plan + gap analysis
│   ├── DRY_VIOLATION.md            ← 43-instance boilerplate tracker
│   ├── functionalities.md          ← Streamlit API reference
│   └── TODO.md                     ← implementation coverage tracker
├── samples/                        ← example user apps
│   ├── class_styling_demo.py       ← Material token showcase + live theme generator
│   ├── oar_demo.py                 ← full dashboard demo (oat.ink)
│   ├── oat_sample.py               ← oat.ink component playground
│   ├── demo_app.py
│   ├── demo_new_features.py
│   ├── test_app.py / test_layouts.py / test_new_components.py / test_widgets.py
│   └── cgpa_calc.py
├── src/
│   └── mxlit/                      ← installable package
│       ├── __init__.py             ← public API surface
│       ├── cli.py                  ← `mxlit run` entry point
│       ├── server.py               ← FastAPI app (routes, SSE, state)
│       ├── context.py              ← per-request AppContext
│       ├── state.py                ← SessionState (global, in-memory)
│       ├── components/
│       │   ├── charts.py           ← line/bar/area/scatter charts
│       │   ├── data.py             ← dataframe, table, json, metric
│       │   ├── layout.py           ← sidebar, columns, tabs, expander
│       │   ├── media.py            ← image, audio, video, logo
│       │   ├── status.py           ← error, warning, info, success
│       │   ├── text.py             ← write, markdown, title, latex …
│       │   ├── theme.py            ← mt.theme() — live theme API
│       │   └── widgets.py          ← button, slider, selectbox …
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
│           └── components.html     ← Jinja2 macro component renderer
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

Best fit for mxlit today: one process owns all in-memory state and SSE queues.

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

When horizontal scaling is needed, in-memory state must be externalised.

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
# ── Build stage ────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir hatchling

COPY pyproject.toml uv.lock ./
COPY src/ src/

RUN pip wheel --no-cache-dir --wheel-dir /wheels .

# ── Runtime stage ───────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels mxlit \
    && rm -rf /wheels

COPY samples/ samples/

EXPOSE 8501

ENV MXLIT_SCRIPT=/app/samples/demo_app.py \
    HOST=0.0.0.0 \
    PORT=8501

CMD ["sh", "-c", "mxlit run $MXLIT_SCRIPT --host $HOST --port $PORT"]
```

**Build & run locally:**

```bash
docker build -t mxlit-app .
docker run -p 8501:8501 -e MXLIT_SCRIPT=/app/samples/demo_app.py mxlit-app
# Open http://localhost:8501
```

---

## 4. Platform Deployment Configs

### 4.1 Fly.io

Fly.io is the recommended platform for mxlit: it supports persistent TCP connections
(required for SSE), long-running processes, and private Redis via `fly redis create`.

**`fly.toml`** (place in repository root):

```toml
app = "mxlit-app"
primary_region = "iad"          # change to your nearest region

[build]
  dockerfile = "Dockerfile"

[env]
  PORT       = "8501"
  HOST       = "0.0.0.0"
  # MXLIT_SCRIPT is set as a Fly secret (see below)

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

**Deploy steps:**

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
fly launch --no-deploy
fly secrets set MXLIT_SCRIPT=/app/samples/demo_app.py
fly deploy
fly open
```

**Scaling to multiple instances on Fly.io:**

```bash
fly redis create --name mxlit-redis --region iad
fly secrets set REDIS_URL=$(fly redis status mxlit-redis --json | jq -r '.privateUrl')
fly scale count 2
```

---

### 4.2 Railway

Railway auto-detects the `Dockerfile` and requires zero extra config files.

**`railway.toml`** (optional — place in repository root):

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

**Deploy steps:**

```bash
npm i -g @railway/cli
railway login
railway init
railway variables set MXLIT_SCRIPT=/app/samples/demo_app.py
railway variables set PORT=8501
railway up
```

> **Note:** Railway exposes a single port via `$PORT`. The `Dockerfile` CMD already
> reads `$PORT`, so no changes are needed.

---

### 4.3 AWS App Runner

**`apprunner.yaml`** (place in repository root):

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
    env: PORT
  env:
    - name: MXLIT_SCRIPT
      value: samples/demo_app.py
    - name: HOST
      value: "0.0.0.0"
    - name: PORT
      value: "8080"
```

> **App Runner SSE caveat:** App Runner has a default idle connection timeout of 120 s.
> Send a heartbeat comment (`": heartbeat\n\n"` every 60 s) from `server.py`'s
> `event_generator` to keep SSE connections alive.

---

## 5. Persistent Session State (Distributed)

`state.py` holds a single global `SessionState` (a Python dict). This breaks when
the process restarts or multiple instances run behind a load balancer.

**Redis-backed drop-in replacement for `src/mxlit/state.py`:**

```python
import os, json, redis

_redis = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
SESSION_TTL = 3600  # seconds

class SessionState:
    def __init__(self, session_id: str = "global"):
        super().__setattr__('_sid', f"mxlit:session:{session_id}")

    def _get_all(self) -> dict:
        raw = _redis.get(self._sid)
        return json.loads(raw) if raw else {}

    def _save(self, data: dict):
        _redis.setex(self._sid, SESSION_TTL, json.dumps(data))

    def get(self, name, default=None):   return self._get_all().get(name, default)
    def __contains__(self, name):        return name in self._get_all()
    def __getitem__(self, name):         return self._get_all()[name]

    def __setitem__(self, name, value):
        data = self._get_all(); data[name] = value; self._save(data)

    def __getattr__(self, name):
        val = self._get_all().get(name)
        if val is None: raise AttributeError(f"No session attribute '{name}'")
        return val

    def __setattr__(self, name, value):  self[name] = value
    def clear(self):                     _redis.delete(self._sid)
```

**Session-ID wiring in `server.py`:**

```python
from fastapi import Cookie
from mxlit.state import SessionState
import uuid

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, mxlit_sid: str = Cookie(default=None)):
    sid = mxlit_sid or str(uuid.uuid4())
    response = templates.TemplateResponse("base.html", {"request": request})
    response.set_cookie("mxlit_sid", sid, httponly=True, samesite="lax")
    return response
# Pass `sid` into each handler and construct SessionState(sid) per request.
```

---

## 6. SSE in a Distributed Environment

`server.py` stores active SSE queues in an in-process set (`sse_clients`).
A `/modify` call on instance A cannot push events to clients on instance B.

**Redis Pub/Sub fanout replacement:**

```python
import asyncio, os
import redis.asyncio as aioredis

REDIS_URL  = os.environ.get("REDIS_URL", "redis://localhost:6379")
SSE_CHANNEL = "mxlit:sse:global"

async def _publish_html(html: str):
    async with aioredis.from_url(REDIS_URL) as r:
        await r.publish(SSE_CHANNEL, html)

@app.get("/events")
async def global_events(request: Request):
    async def event_generator():
        async with aioredis.from_url(REDIS_URL) as r:
            pubsub = r.pubsub()
            await pubsub.subscribe(SSE_CHANNEL)
            try:
                while True:
                    if await request.is_disconnected(): break
                    msg = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=30
                    )
                    if msg:
                        html_str = msg["data"].decode()
                        lines = "\n".join(f"data: {l}" for l in html_str.split("\n"))
                        yield f"{lines}\n\n"
                    else:
                        yield ": heartbeat\n\n"   # keeps ALB/App Runner alive
            finally:
                await pubsub.unsubscribe(SSE_CHANNEL)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### SSE Load-Balancer Checklist

| Concern | Recommendation |
|---|---|
| Sticky sessions | Enable if Redis Pub/Sub is not yet wired |
| Connection timeout | Set ALB/App Runner idle timeout ≥ 300 s; send `: heartbeat` every 60 s |
| TLS termination | Terminate at load balancer; backend runs plain HTTP |
| Reconnection | HTMX `sse.js` reconnects automatically on drop |
| Scaling to zero | Disable — cold starts break SSE (`min_machines_running = 1`) |

---

## 7. Deployment Checklist

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
- [ ] Enable health-check route (`GET /` returns 200 — sufficient)
- [ ] Set `min_machines_running = 1` (or equivalent) to prevent scale-to-zero

---

## 8. Theme System — `mt.theme()` and Material Design Tokens

### 8.1 How It Works

`mt.theme()` is the single API for reading and overriding the live colour palette.
It reads `session_state[THEME_KEY]`, merges any overrides, persists the result back,
and returns the full resolved token dict for use in Python:

```python
_t = mt.theme()                              # read current palette
_t = mt.theme({"schemes.light.primary": "#9333ea"})  # override + read
primary_hex = _t["schemes.light.primary"]
```

The Jinja2 template in `components.html` emits the resolved palette as CSS variables
on every HTMX response — no manual `mt.html()` injection is needed.

### 8.2 Token Keys

Keys are **dot-notation paths** that mirror `constants/theme.json`, e.g.:

| Token key | CSS variable |
|---|---|
| `schemes.light.primary` | `--primary` |
| `schemes.light.secondary` | `--secondary` |
| `schemes.light.background` | `--background` / `--card` |
| `schemes.light.onBackground` | `--foreground` / `--card-foreground` |

All 386 hex-colour entries from `theme.json` are valid keys (`_DEFAULTS` in
`constants/theme.py`). Passing an unrecognised key raises `ValueError`.

### 8.3 Color-Picker Widget Absorption

`color_picker` widgets write back to `session_state` using the **flat-key alias**:

```
"theme_" + token_key.replace(".", "_")
```

Example — `mt.color_picker("Primary", value=p, key="theme_schemes_light_primary")`
writes `session_state["theme_schemes_light_primary"]`, which `mt.theme()` absorbs
and deletes on the next script re-run. `_FLAT_KEYS` (in `constants/theme.py`) maps
every valid alias back to its dot-notation path.

### 8.4 Preset Pattern

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

## 9. OAT Integration — oat.ink UI Patterns

### 9.1 Styling Philosophy

oat.ink styles elements through **semantic HTML attributes**, not utility classes.
The correct approach is:

| ✅ Correct (OAT) | ❌ Wrong (hardcoded Tailwind) |
|---|---|
| `data-variant="error"` | `class="bg-red-100 text-red-700"` |
| `data-field` wrapper | `class="border rounded px-2"` |
| `role="switch"` | `class="toggle-switch"` |
| `aria-busy="true"` | `class="loading"` |

Use `class_=` only for **layout** (`w-full`, `mt-4`, `rounded-lg`) and **typography**
adjustments (`text-xs`, `font-bold`). Never use Tailwind colour classes for semantic
meaning — use OAT variant attributes instead.

### 9.2 Key OAT Attributes

| HTML attribute | Values | Rendered by |
|---|---|---|
| `data-variant` | `success` `warning` `error` `danger` `secondary` | alert, badge, button, avatar |
| `data-field` | `""` (standard) `"error"` (red border) | all form field wrappers |
| `role="alert"` | — | `error`, `warning`, `info`, `success` banners |
| `role="switch"` | — | `toggle` component |
| `aria-busy="true"` | — | spinner / loading overlay |
| `data-spinner` | `small` `large` `overlay` | spinner size modifier |
| `title="…"` | tooltip text | any element — OAT renders smooth tooltip |

### 9.3 Current Component → OAT Mapping (implemented)

| mxlit function | OAT element |
|---|---|
| `mt.error/warning/info/success` | `<div role="alert" data-variant="…">` |
| `mt.button` | `<button data-variant="secondary">` |
| `mt.toggle` | `<input type="checkbox" role="switch">` |
| `mt.text_input` / `mt.text_area` / etc. | `<input>` inside `<label data-field>` |
| `mt.tabs` | `<ot-tabs>` WebComponent |
| `mt.sidebar` | `<aside data-sidebar>` in `[data-sidebar-layout]` |
| `mt.expander` | `<details><summary>` |
| `mt.badge` | `<span class="badge" data-variant="…">` |

---

## 10. Component Architecture Roadmap (`docs/PLAN.md`)

### 10.1 Current Pattern (use this today)

Every component function in `components/*.py` follows this boilerplate:

```python
def my_component(label: str, class_: str = "") -> None:
    from mxlit.context import get_context
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "my_component", "label": label, "class_": class_})
    else:
        print(f"[MY_COMPONENT] {label}")
```

For **widgets** (return a value from `session_state`):

```python
def my_widget(label: str, value: str = "", key: str = None, class_: str = "") -> str:
    import hashlib
    widget_key = key or hashlib.md5(f"my_widget-{label}".encode()).hexdigest()
    from mxlit.context import get_context
    from mxlit.state import session_state
    current = session_state.get(widget_key, value)
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "my_widget", "label": label, "value": current,
                           "key": widget_key, "class_": class_})
    return current
```

### 10.2 Planned Refactor — `BaseComponent` (Phase 1 + 2)

`docs/PLAN.md` §2 specifies a `BaseComponent` dataclass in `src/mxlit/components/base.py`
that eliminates the 43-instance boilerplate. Key types:

| Class | Purpose |
|---|---|
| `ComponentType(str, Enum)` | Typed registry of all component type strings |
| `HtmxProps` dataclass | All HTMX attributes (`hx-post`, `hx-target`, `hx-swap`, `hx-trigger`, …) |
| `OatProps` dataclass | OAT semantic attrs (`data-variant`, `role`, `data-field`, `aria-busy`, …) |
| `BaseComponent` dataclass | Root: constructs, registers in `__post_init__`, serializes via `to_dict()` |
| `CompositeComponent(BaseComponent)` | Deferred registration via `with` block; nests children |
| `@component` decorator | Turns a props-builder into a display component (no return value) |
| `@widget_component` decorator | Turns a props-builder into a stateful widget (returns value) |

**Do not implement `base.py` yet** — existing components still use the boilerplate pattern.
New components added before the migration should also use the boilerplate pattern for consistency.
See `docs/PLAN.md` §7 (Migration Checklist) for the step-by-step migration guide.

### 10.3 Targeted Update Strategy (Section 10 of PLAN.md)

Currently every widget interaction replaces all of `#app-root` (full re-render).
The plan is for each widget to target only its own wrapper via `hx-target="#mx-{key}"` and
`hx-swap="outerHTML"`. This requires:

1. Wrap every rendered component in `<div id="mx-{{ comp.id }}">` in `components.html`
2. Widgets switch from `hx-target="#app-root"` → `hx-target="#mx-{{ comp.id }}"`
3. Buttons use `type="button"` + `hx-target="#mx-main"` + `hx-include="[name]"`
4. `#app-root` div keeps only `hx-trigger="load"` for initial render (no duplicate `hx-post`)

---

## 11. oat.ink Gap Analysis — Missing Components

Audited against [oat.ink/components](https://oat.ink/components/) on 2026-05-28.
Full details in `docs/PLAN.md` §5.4.

### 11.1 Missing UI Primitives (14 items)

| # | Function | Priority | Implementation |
|---|----------|----------|----------------|
| 1 | `mt.card(header, footer)` | 🔴 High | `<article class="card">` — CompositeComponent |
| 2 | `mt.spinner(size)` | 🔴 High | `<div aria-busy="true" data-spinner="…">` |
| 3 | `mt.progress(value, max)` | 🔴 High | Native `<progress value max>` |
| 4 | `mt.skeleton(variant)` | 🟡 Medium | `<div role="status" class="skeleton line\|box">` |
| 5 | `mt.avatar(src, initials, size)` | 🟡 Medium | `<figure data-variant="avatar">` |
| 6 | `mt.avatar_group(size)` | 🟡 Medium | CompositeComponent |
| 7 | `mt.meter(value, min, max, …)` | 🟡 Medium | Native `<meter>` |
| 8 | `mt.breadcrumb(items)` | 🟡 Medium | `<nav aria-label="Breadcrumb"><ol class="unstyled hstack">` |
| 9 | `mt.button_group(labels)` | 🟡 Medium | `<menu class="buttons">` |
| 10 | `mt.toast(message, variant, …)` | 🟡 Medium | `ot.toast()` JS call via SSE |
| 11 | `mt.pagination(total, current)` | 🟡 Medium | Widget — returns new page number |
| 12 | `mt.dialog(id, title)` | 🟠 Low | `<dialog closedby="any">` — CompositeComponent |
| 13 | `mt.dropdown(label)` | 🟠 Low | `<ot-dropdown>` WebComponent |
| 14 | `mt.grid(cols)` | 🟠 Low | `<div class="container"><div class="row">` |

### 11.2 Missing Form Input Variants (5 items)

| # | Function | Priority | Notes |
|---|----------|----------|-------|
| 15 | `mt.email_input(label, value, key)` | 🔴 High | `type="email"` — browser validation |
| 16 | `mt.password_input(label, key)` | 🔴 High | `type="password"` — never stored in session |
| 17 | `mt.datetime_input(label, value, key)` | 🟡 Medium | `type="datetime-local"` |
| 18 | `mt.file_input(label, accept, key)` | 🟡 Medium | `type="file"` — needs multipart encoding |
| 19 | `mt.input_group(prefix, suffix)` | 🟠 Low | `<fieldset class="group">` |

> **Implementation order:** Start with High-priority leaf components (spinner, progress,
> email_input, password_input) — each is a single PR with no dependency on CompositeComponent.
