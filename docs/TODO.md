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
- [~] `st.columns(vertical_alignment=)` — parameter accepted, not applied in template
- [x] `st.tabs()`
- [x] `st.expander()`
- [x] `st.container()`
- [x] `st.container(horizontal=True)`
- [ ] `st.popover()`
- [ ] `st.space()`

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
- [ ] `st.multiselect()`
- [ ] `st.select_slider()`
- [ ] `st.datetime_input()`
- [ ] `st.time_input()`
- [ ] `st.file_uploader()`
- [ ] `st.audio_input()`
- [ ] `st.camera_input()`
- [ ] `st.download_button()`
- [ ] `st.link_button()`
- [ ] `st.page_link()`
- [ ] `st.data_editor()`
- [ ] `st.feedback()`
- [ ] `st.pills()`
- [ ] `st.segmented_control()`
- [ ] `disabled=True` support on all widgets

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
- [ ] `st.get_option()` / `st.set_option()`
- [ ] `st.set_page_config()`
- [ ] `st.query_params`

---

## Connect to Data Sources

- [ ] `st.connection()` (SQL, Snowflake, etc.)
- [ ] `BaseConnection` custom connection API

---

## Optimize Performance (Caching)

- [ ] `@st.cache_data`
- [ ] `@st.cache_resource`

---

## Display Progress & Status

- [x] `st.error()`
- [x] `st.warning()`
- [x] `st.info()`
- [x] `st.success()`
- [x] `st.exception()`
- [ ] `st.spinner()`
- [ ] `st.progress()`
- [ ] `st.status()` *(expandable status container)*
- [ ] `st.toast()`
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

## Summary

| Category | Done | Total |
|---|---|---|
| Display Text | 11 | 11 |
| Display Data | 4 | 4 |
| Display Media | 4 | 5 |
| Display Charts | 4 | 12 |
| Layout | 7 | 9 |
| Control Flow | 2 | 7 |
| Widgets | 11 | 25 |
| Chat | 0 | 2 |
| Mutate Data | 0 | 1 |
| Display Code | 0 | 1 |
| Placeholders & Options | 0 | 5 |
| Data Sources | 0 | 2 |
| Caching | 0 | 2 |
| Progress & Status | 5 | 11 |
| Auth & Context | 0 | 9 |
| Magic Commands | 0 | 1 |
| **Total** | **48** | **107** |
