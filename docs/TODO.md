# mxlit — Streamlit API Coverage TODO

Tracks implementation status of every API item listed in `functionalities.md`.
- [x] = implemented (validated against ComponentType enum, template branches, and `__init__.py` exports)
- [ ] = not yet implemented
- [~] = partially implemented (noted inline)

Complexity tags on unimplemented items:
- `[Easy]` — 1–2 files, mirrors an existing pattern, ≤ 30 min
- `[Medium]` — new component + template branch, bounded scope, ≤ 2 h
- `[Hard]` — new architecture, external dependency, or non-trivial JS integration

---

## Display Text

- [x] `st.write()`
- [x] `st.write_stream()`
- [x] `st.text()`
- [x] `st.markdown()`
- [x] `st.latex()` *(rendered as raw `$$..$$` — no KaTeX/MathJax loaded yet)*
- [x] `st.title()`
- [x] `st.header()`
- [x] `st.subheader()`
- [x] `st.code()`
- [x] `st.badge()`
- [x] `st.html()`

---

## Display Data

- [x] `st.dataframe()`
- [x] `st.table()`
- [x] `st.json()`
- [x] `st.metric()`

---

## Display Media

- [x] `st.image()`
- [x] `st.logo()`
- [x] `st.audio()`
- [x] `st.video()` *(subtitles parameter not yet supported)*
- [ ] `st.pdf()` `[Easy]` — `<embed>` tag, identical pattern to `st.image()` / `st.audio()`

---

## Display Charts

**Implemented**
- [x] `st.line_chart()`
- [x] `st.area_chart()`
- [x] `st.scatter_chart()`
- [~] `st.bar_chart()` — `horizontal=True` accepted, prop passed through, but `indexAxis: 'y'` not wired in Chart.js config block in `components.html:387`

**Not implemented**
- [ ] `st.map()` `[Medium]` — add Leaflet.js CDN to `base.html`; new component renders `<div id>` + JS init with lat/lon columns
- [ ] `st.pyplot()` `[Medium]` — server-side: `fig.savefig(buf)` → base64 PNG → renders as `<img>`; no new JS needed
- [ ] `st.graphviz_chart()` `[Medium]` — call `graphviz.Source.pipe(format='svg')` server-side; render raw SVG in template
- [ ] `st.altair_chart()` `[Hard]` — needs `vega-embed` JS (CDN); pass Vega-Lite JSON spec; `on_select` adds event callback complexity
- [ ] `st.vega_lite_chart()` `[Hard]` — same `vega-embed` path as `altair_chart`; spec differs slightly
- [ ] `st.plotly_chart()` `[Hard]` — needs Plotly.js CDN (~3 MB); pass `fig.to_json()` spec; `on_select` adds JS→SSE callback
- [ ] `st.pydeck_chart()` `[Hard]` — needs deck.gl CDN; full 3-D map rendering; rarely used
- [ ] Chart `on_select` event handling (`plotly_chart`, `altair_chart`, `vega_lite_chart`) `[Hard]` — requires JS event listener → POST to `/interact` with selection payload; new server route

---

## Layout

- [x] `st.sidebar` / `with st.sidebar:`
- [x] `st.columns(n)` — equal columns
- [x] `st.columns([3, 1, 1])` — weighted columns
- [~] `st.columns(vertical_alignment=)` — prop accepted and stored in component dict but `align-items` CSS never applied in `components.html` flex wrapper `[Easy]` — add `align-items: {{ 'flex-start' if va == 'top' else 'center' if va == 'center' else 'flex-end' }}` to column flex container
- [x] `st.tabs()`
- [x] `st.expander()`
- [x] `st.container()`
- [x] `st.container(horizontal=True)`
- [x] `st.popover()` → `mt.popover(label)` — HTML Popover API CompositeComponent
- [x] `st.space()` → `mt.space(n)` — vertical whitespace in rem units

---

## Control Flow

**Implemented**
- [x] `st.stop()`
- [x] `st.rerun()`

**Not implemented**
- [ ] `st.form()` / `st.form_submit_button()` `[Medium]` — wrap children in `<form>` CompositeComponent; submit batches all field values in one POST; no per-field HTMX triggers inside form
- [ ] `@st.dialog()` `[Medium]` — decorator variant of `mt.dialog()` CompositeComponent; `mt.dialog()` already exists, needs `@`-decorator wrapper + trigger wiring
- [ ] `st.switch_page()` `[Hard]` — requires multi-page routing system (does not exist); depends on `st.navigation()` / `st.Page()`
- [ ] `st.navigation()` / `st.Page()` `[Hard]` — full multi-page architecture: separate script-per-page, URL routing in `server.py`, nav sidebar integration
- [ ] `@st.fragment` `[Hard]` — partial script re-execution: isolate a decorated function's component subtree; requires AST/execution scope changes in `server.py`

---

## Interactive Widgets

**Implemented**
- [x] `st.button()`
- [x] `st.checkbox()`
- [x] `st.radio()`
- [x] `st.selectbox()`
- [x] `st.toggle()`
- [x] `st.slider()`
- [x] `st.text_input()`
- [x] `st.number_input()`
- [x] `st.text_area()`
- [x] `st.date_input()`
- [x] `st.color_picker()`
- [x] `st.datetime_input()` → `mt.datetime_input()` *(datetime-local input)*
- [~] `st.file_uploader()` → `mt.file_input()` *(browser-side only; no server-side file object yet)*
- [x] `st.multiselect()` → `mt.multiselect(label, options, default, key, disabled)`
- [x] `st.select_slider()` → `mt.select_slider(label, options, value, key, disabled)`
- [x] `st.time_input()` → `mt.time_input(label, value, key, disabled)`
- [x] `st.download_button()` → `mt.download_button(label, data, file_name, mime)`
- [x] `st.link_button()` → `mt.link_button(label, url, new_tab)`
- [x] `st.feedback()` → `mt.feedback(label, sentiment, key)` — thumbs or stars
- [x] `st.pills()` → `mt.pills(label, options, index, key, disabled)`
- [x] `disabled=True` support on all widgets

**Not implemented**
- [ ] `st.page_link()` `[Easy]` — thin alias over `mt.link_button()` with optional `icon=` param; `<a role="button">` already renders correctly
- [ ] `st.segmented_control()` `[Easy]` — `mt.pills()` covers identical use-case; add alias + map `selection_mode` param
- [ ] `st.audio_input()` `[Hard]` — browser MediaRecorder API; recorded blob must be uploaded via multipart POST; needs new server route for blob storage
- [ ] `st.camera_input()` `[Hard]` — `getUserMedia()` + canvas capture; same upload path as `audio_input`; needs JS-heavy component
- [ ] `st.data_editor()` `[Hard]` — interactive editable data grid; requires AG Grid or similar; cell-edit events → POST; significant JS + new server-side diff logic

---

## Chat

- [ ] `st.chat_message()` `[Medium]` — bubble layout: `<div data-variant="…">` with avatar + role label; CompositeComponent pattern; no new JS needed
- [ ] `st.chat_input()` `[Medium]` — sticky-bottom `<input>` / `<textarea>` + submit triggers full re-render via HTMX POST; integrates with `session_state` for history

---

## Mutate Data

- [ ] `element.add_rows()` on dataframe / chart elements `[Hard]` — requires element-reference API (components currently have no handles); needs SSE push of row delta + Chart.js `data.push()` call

---

## Display Code

- [ ] `st.echo()` `[Medium]` — Python context manager using `inspect.getsource()` + AST line-range extraction; renders captured block via `mt.code()`; no new template work needed

---

## Placeholders & Options

- [x] `st.get_option()` / `st.set_option()` → `mt.get_option(key)` / `mt.set_option(key, value)`
- [~] `st.set_page_config()` `[Medium]` — `mt.page_config()` exists but only sets Tailwind CSS classes on layout elements; extend to accept `page_title`, `page_icon`, `layout`, `initial_sidebar_state` and inject into `base.html` via context vars
- [ ] `st.empty()` `[Hard]` — Streamlit's `st.empty()` returns an updatable single-slot container; `mt.empty()` is a static placeholder div; requires element-mutation API (same dependency as `add_rows()`)
- [ ] `st.help()` `[Easy]` — `pydoc.render_doc(obj, renderer=pydoc.plaintext)` → render via `mt.code()`; pure Python, no template changes
- [ ] `st.query_params` `[Medium]` — expose FastAPI `request.query_params` as a dict-like object on `AppContext`; needs read + write (redirect with updated QS) semantics

---

## Connect to Data Sources

- [ ] `st.connection()` `[Hard]` — plugin-based connection registry (SQL, Snowflake, etc.); requires `BaseConnection` ABC + caching layer + credential management
- [ ] `BaseConnection` custom connection API `[Hard]` — abstract base class + `connect()` / `query()` / `reset()` lifecycle; depends on `st.connection()` registry

---

## Optimize Performance (Caching)

- [x] `@st.cache_data` → `@mt.cache_data` — `functools.lru_cache` wrapper for data functions
- [x] `@st.cache_resource` → `@mt.cache_resource` — `functools.lru_cache` wrapper for shared resources

---

## Display Progress & Status

- [x] `st.error()`
- [x] `st.warning()`
- [x] `st.info()`
- [x] `st.success()`
- [x] `st.exception()`
- [x] `st.spinner()` → `mt.spinner(size)` *(aria-busy spinner, small/large/overlay)*
- [x] `st.progress()` → `mt.progress(value, max)` *(native `<progress>`; indeterminate when value omitted)*
- [x] `st.toast()` → `mt.toast(message, title, variant, placement, duration)` *(calls `ot.toast()` JS)*
- [x] `st.status()` → `mt.status(label, state)` — expandable container with running/complete/error indicator
- [ ] `st.balloons()` `[Easy]` — trigger a CSS confetti animation via a JS call injected through SSE; same pattern as `mt.toast()`
- [ ] `st.snow()` `[Easy]` — CSS snowfall animation; same JS-injection pattern as `st.balloons()`

---

## Personalize Apps (Auth & Context)

- [ ] `st.user` (`is_logged_in`, `name`, etc.) `[Hard]` — requires OAuth / auth-provider integration; no auth layer exists yet
- [ ] `st.login()` / `st.logout()` `[Hard]` — OAuth flow (redirect → callback → session cookie); depends on auth provider
- [ ] `st.context.cookies` `[Medium]` — expose `request.cookies` via a `ctx.context` namespace object in `AppContext`
- [ ] `st.context.headers` `[Medium]` — expose `request.headers`; same `ctx.context` namespace
- [ ] `st.context.ip_address` `[Medium]` — `request.client.host`; same namespace
- [ ] `st.context.locale` `[Medium]` — parse `Accept-Language` header; same namespace
- [ ] `st.context.theme` `[Medium]` — expose current resolved theme dict; bridge to existing `mt.theme()` API
- [ ] `st.context.timezone` / `timezone_offset` `[Medium]` — JS `Intl.DateTimeFormat().resolvedOptions().timeZone` → POST on load → store in session
- [ ] `st.context.url` / `is_embedded` `[Medium]` — `request.url` + `Referer` header check; same namespace

> **Note:** All `st.context.*` items share the same implementation pattern (expose request data via a namespace object on `AppContext`) and can be batched into one PR. Auth items (`st.user`, `st.login/logout`) are independent and require an auth provider decision first.

---

## Magic Commands

- [ ] Implicit `st.write()` via bare expressions (magic mode) `[Hard]` — requires AST transformation of the user script before execution to wrap bare expressions in `mt.write()` calls; changes `cli.py` script loading

---

## OAT UI Extensions (mxlit-specific, no Streamlit equivalent)

Components from the oat.ink component library gap analysis — implemented in `src/mxlit/components/`.

### UI Primitives
- [x] `mt.card(header, footer)` — `<article class="card">` CompositeComponent
- [x] `mt.spinner(size)` — `<div aria-busy="true" data-spinner="…">`
- [x] `mt.skeleton(variant)` — `<div role="status" class="skeleton line|box">`
- [x] `mt.meter(value, min, max, low, high, optimum)` — native `<meter>`
- [x] `mt.avatar(src, initials, size)` — `<figure data-variant="avatar">`
- [x] `mt.avatar_group(avatars, size)` — stacked avatar group
- [x] `mt.breadcrumb(items)` — `<nav aria-label="Breadcrumb"><ol class="unstyled hstack">`
- [x] `mt.button_group(labels, key_prefix)` — `<menu class="buttons">`
- [x] `mt.toast(message, title, variant, placement, duration)` — `ot.toast()` JS call
- [x] `mt.dialog(title, trigger_label)` — `<dialog closedby="any">` CompositeComponent
- [x] `mt.dropdown(label, items)` — `<ot-dropdown>` WebComponent
- [x] `mt.grid()` — `<div class="container"><div class="row">` CompositeComponent
- [x] `mt.pagination(total_pages, current_page)` — returns current page (widget)

### Form Input Variants
- [x] `mt.email_input(label, value, key)` — `type="email"` with browser validation
- [x] `mt.password_input(label, key)` — `type="password"` (never stored in session)
- [x] `mt.input_group(prefix, suffix)` — `<fieldset class="group">` CompositeComponent
- [x] `mt.file_input(label, accept, key)` — `type="file"` with multipart encoding

### Auto-Refresh / Timers
- [x] `mt.setInterval(sync_time)` — HTMX polling context manager (`every Ns` trigger)
- [x] `mt.setTimeout(delay)` — one-shot HTMX trigger context manager

### Spacer / Placeholder
- [x] `mt.space(n)` — vertical whitespace (n × rem)
- [x] `mt.empty()` — structural empty placeholder div *(not the same as `st.empty()` updateable container)*

### Overlay / Status
- [x] `mt.popover(label)` — HTML Popover API CompositeComponent
- [x] `mt.status(label, state)` — expandable status container (running/complete/error)

### New Widgets
- [x] `mt.multiselect(label, options, default, key, disabled)` — `<select multiple>`
- [x] `mt.select_slider(label, options, value, key, disabled)` — range input with discrete options
- [x] `mt.time_input(label, value, key, disabled)` — `<input type="time">`
- [x] `mt.link_button(label, url, new_tab)` — `<a role="button">` hyperlink
- [x] `mt.download_button(label, data, file_name, mime)` — data-URI download
- [x] `mt.pills(label, options, index, key, disabled)` — pill-shaped single-select
- [x] `mt.feedback(label, sentiment, key)` — thumbs 👍/👎 or stars ★ rating

### Caching + Options
- [x] `@mt.cache_data` / `@mt.cache_resource` — `functools.lru_cache` decorator helpers
- [x] `mt.get_option(key)` / `mt.set_option(key, value)` — runtime option dictionary

---

## Quick Wins (Easy items, pick up any sprint)

Items requiring ≤ 30 min each, no new architecture:

| Item | Where | What to do |
|---|---|---|
| `st.pdf()` | `media.py` + `components.html` | Add `<embed src type="application/pdf">` — mirrors `st.audio()` exactly |
| `st.balloons()` | `__init__.py` + `components.html` | JS confetti call via SSE — mirrors `mt.toast()` pattern |
| `st.snow()` | `__init__.py` + `components.html` | JS snow call via SSE — mirrors `mt.toast()` pattern |
| `st.page_link()` | `widgets.py` + `components.html` | Alias `mt.link_button()` with `icon=` param |
| `st.segmented_control()` | `widgets.py` | Alias `mt.pills()` with `selection_mode` param |
| `st.help()` | `__init__.py` | `pydoc.render_doc(obj)` → `mt.code()` — pure Python |
| `st.columns(vertical_alignment=)` | `components.html` line ~835 | Apply `align-items` CSS to flex wrapper using existing `comp.vertical_alignment` prop |
| `st.bar_chart(horizontal=True)` | `components.html` line ~370 | Wire `indexAxis: 'y'` in Chart.js config when `comp.horizontal` is true |

---

## Summary

| Category | Done | Total | Notes |
|---|---|---|---|
| Display Text | 11 | 11 | ✅ |
| Display Data | 4 | 4 | ✅ |
| Display Media | 4 | 5 | `st.pdf` — Easy |
| Display Charts | 3 | 12 | 1 partial (`bar_chart`); 1 Medium (`map`, `pyplot`, `graphviz`); 4 Hard |
| Layout | 8 | 9 | 1 partial (`vertical_alignment`) — Easy fix |
| Control Flow | 2 | 7 | 1 Medium (`form`, `@dialog`); 3 Hard |
| Widgets | 20 | 25 | 2 Easy (`page_link`, `segmented_control`); 3 Hard |
| Chat | 0 | 2 | Both Medium |
| Mutate Data | 0 | 1 | Hard |
| Display Code | 0 | 1 | Medium (`st.echo`) |
| Placeholders & Options | 2 | 5 | 1 partial (`set_page_config`); 1 Easy (`help`); 1 Medium; 1 Hard |
| Data Sources | 0 | 2 | Both Hard |
| Caching | 2 | 2 | ✅ |
| Progress & Status | 9 | 11 | 2 Easy (`balloons`, `snow`) |
| Auth & Context | 0 | 9 | 2 Hard (auth); 7 Medium (context) |
| Magic Commands | 0 | 1 | Hard |
| **Streamlit Total** | **65** | **107** | *(TODO count corrected: 2 items were [~] not [x])* |
| **OAT Extensions** | **32** | **32** | ✅ all implemented |
| **Grand Total** | **97** | **139** | |

### By complexity (unimplemented only)

| Tier | Count | Items |
|---|---|---|
| Easy | 8 | `pdf`, `balloons`, `snow`, `page_link`, `segmented_control`, `help`, `vertical_alignment` fix, `bar_chart horizontal` fix |
| Medium | 13 | `map`, `pyplot`, `graphviz`, `form`, `@dialog`, `chat_message`, `chat_input`, `echo`, `set_page_config`, `query_params`, all 7 `st.context.*` items |
| Hard | 14 | `altair`, `vega_lite`, `plotly`, `pydeck`, `on_select`, `switch_page`, `navigation`, `fragment`, `audio_input`, `camera_input`, `data_editor`, `add_rows`, `st.empty`, `connection`, `auth`, `magic` |
