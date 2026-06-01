# mxlit — Streamlit API Coverage TODO

Tracks implementation status of every API item listed in `functionalities.md`.
- [x] = implemented
- [ ] = not yet implemented
- [~] = partially implemented (noted inline)

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
- [ ] `st.pdf()`

---

## Display Charts

- [x] `st.line_chart()`
- [x] `st.area_chart()`
- [x] `st.bar_chart()` *(`horizontal=True` accepted but Chart.js `indexAxis` not wired)*
- [x] `st.scatter_chart()`
- [ ] `st.map()`
- [ ] `st.altair_chart()`
- [ ] `st.plotly_chart()`
- [ ] `st.graphviz_chart()`
- [ ] `st.pydeck_chart()`
- [ ] `st.pyplot()`
- [ ] `st.vega_lite_chart()`
- [ ] Chart `on_select` event handling (`plotly_chart`, `altair_chart`, `vega_lite_chart`)

---

## Layout

- [x] `st.sidebar` / `with st.sidebar:`
- [x] `st.columns(n)` — equal columns
- [x] `st.columns([3, 1, 1])` — weighted columns
- [~] `st.columns(vertical_alignment=)` — parameter accepted, CSS `align-items` not yet applied in template
- [x] `st.tabs()`
- [x] `st.expander()`
- [x] `st.container()`
- [x] `st.container(horizontal=True)`
- [x] `st.popover()` → `mt.popover(label)` — HTML Popover API CompositeComponent
- [x] `st.space()` → `mt.space(n)` — vertical whitespace in rem units

---

## Control Flow

- [x] `st.stop()`
- [x] `st.rerun()`
- [ ] `st.switch_page()`
- [ ] `st.navigation()` / `st.Page()`
- [ ] `st.form()` / `st.form_submit_button()`
- [ ] `@st.dialog()`
- [ ] `@st.fragment`

---

## Interactive Widgets

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
- [ ] `st.audio_input()`
- [ ] `st.camera_input()`
- [x] `st.download_button()` → `mt.download_button(label, data, file_name, mime)`
- [x] `st.link_button()` → `mt.link_button(label, url, new_tab)`
- [ ] `st.page_link()`
- [ ] `st.data_editor()`
- [x] `st.feedback()` → `mt.feedback(label, sentiment, key)` — thumbs or stars
- [x] `st.pills()` → `mt.pills(label, options, index, key, disabled)`
- [ ] `st.segmented_control()` *(pills covers same use-case)*
- [x] `disabled=True` support on all widgets

---

## Chat

- [ ] `st.chat_message()`
- [ ] `st.chat_input()`

---

## Mutate Data

- [ ] `element.add_rows()` on dataframe / chart elements

---

## Display Code

- [ ] `st.echo()`

---

## Placeholders & Options

- [ ] `st.empty()`
- [ ] `st.help()`
- [x] `st.get_option()` / `st.set_option()` → `mt.get_option(key)` / `mt.set_option(key, value)`
- [ ] `st.set_page_config()`
- [ ] `st.query_params`

---

## Connect to Data Sources

- [ ] `st.connection()` (SQL, Snowflake, etc.)
- [ ] `BaseConnection` custom connection API

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
- [ ] `st.balloons()`
- [ ] `st.snow()`

---

## Personalize Apps (Auth & Context)

- [ ] `st.user` (`is_logged_in`, `name`, etc.)
- [ ] `st.login()` / `st.logout()`
- [ ] `st.context.cookies`
- [ ] `st.context.headers`
- [ ] `st.context.ip_address`
- [ ] `st.context.locale`
- [ ] `st.context.theme`
- [ ] `st.context.timezone` / `timezone_offset`
- [ ] `st.context.url` / `is_embedded`

---

## Magic Commands

- [ ] Implicit `st.write()` via bare expressions (magic mode)

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
- [x] `mt.empty()` — structural empty placeholder div

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

## Summary

| Category | Done | Total | Notes |
|---|---|---|---|
| Display Text | 11 | 11 | |
| Display Data | 4 | 4 | |
| Display Media | 4 | 5 | `st.pdf` pending |
| Display Charts | 4 | 12 | `st.map`, plotly, altair etc. pending |
| Layout | 9 | 9 | ✅ all done (`popover`, `space` added) |
| Control Flow | 2 | 7 | `switch_page`, `navigation`, `form`, `@dialog`, `@fragment` pending |
| Widgets | 20 | 25 | +multiselect, select_slider, time_input, link_button, download_button, pills, feedback, disabled ✅ |
| Chat | 0 | 2 | |
| Mutate Data | 0 | 1 | |
| Display Code | 0 | 1 | |
| Placeholders & Options | 2 | 5 | +get_option, set_option ✅ |
| Data Sources | 0 | 2 | |
| Caching | 2 | 2 | ✅ cache_data, cache_resource |
| Progress & Status | 9 | 11 | +status() ✅ |
| Auth & Context | 0 | 9 | |
| Magic Commands | 0 | 1 | |
| **Streamlit Total** | **67** | **107** | |
| **OAT Extensions** | **32** | **32** | all implemented |
| **Grand Total** | **99** | **139** | |
