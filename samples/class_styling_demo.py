# -*- coding: utf-8 -*-
"""
class_styling_demo.py
=====================
Kitchen-sink showcase: every mxlit component, the live theme generator,
and Material Design token usage via mt.theme() / constants/theme.json.
Run with:
    mxlit run samples/class_styling_demo.py
"""
import mxlit as mt
import pandas as pd

# ── THEME SETUP ───────────────────────────────────────────────────────────────
# Keys are dot-notation paths into constants/theme.json (schemes.light.*).
_PRESETS = {
    "btn_material": {
        "schemes.light.primary":   "#415F91",
        "schemes.light.secondary": "#565F71",
    },
    "btn_ocean": {
        "schemes.light.primary":   "#0891b2",
        "schemes.light.secondary": "#0d9488",
    },
    "btn_sunset": {
        "schemes.light.primary":   "#ea580c",
        "schemes.light.secondary": "#9333ea",
    },
    "btn_forest": {
        "schemes.light.primary":   "#15803d",
        "schemes.light.secondary": "#92400e",
    },
}
for _pk, _pv in _PRESETS.items():
    if mt.session_state.get(_pk) == "true":
        _t = mt.theme(_pv)
        mt.session_state[_pk] = "false"
        break
else:
    _t = mt.theme()

# ── Core 4 rendering tokens ────────────────────────────────────────────────────
p   = _t["schemes.light.primary"]           # → --primary
s   = _t["schemes.light.secondary"]         # → --secondary
bg  = _t["schemes.light.background"]        # → --background
txt = _t["schemes.light.onBackground"]      # → --foreground

# ── Extended Material tokens (used in swatches and inline HTML) ───────────────
p_on  = _t["schemes.light.onPrimary"]             # text colour on primary
p_ctr = _t["schemes.light.primaryContainer"]      # primary tint container
s_ctr = _t["schemes.light.secondaryContainer"]    # secondary tint container
tert  = _t["schemes.light.tertiary"]              # tertiary accent
t_ctr = _t["schemes.light.tertiaryContainer"]     # tertiary container
err   = _t["schemes.light.error"]                 # error / danger
surf  = _t["schemes.light.surfaceVariant"]        # subtle raised surface
outl  = _t["schemes.light.outline"]               # border / divider colour

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with mt.sidebar:
    mt.title("Theme Generator", class_="text-base font-bold tracking-tight")
    mt.write("Colours sourced from constants/theme.json (schemes.light.*).",
             class_="text-xs mb-3")

    mt.color_picker("Primary",    value=p,    key="theme_schemes_light_primary")
    mt.color_picker("Secondary",  value=s,    key="theme_schemes_light_secondary")
    mt.color_picker("Background", value=bg,   key="theme_schemes_light_background")
    mt.color_picker("Text",       value=txt,  key="theme_schemes_light_onBackground")
    mt.color_picker("Tertiary",   value=tert, key="theme_schemes_light_tertiary")

    mt.write("Quick presets",
             class_="text-xs font-semibold uppercase tracking-wide mt-4 mb-1")
    pa, pb = mt.columns(2)
    with pa:
        mt.button("Material", key="btn_material", class_="w-full text-xs")
        mt.button("Sunset",   key="btn_sunset",   class_="w-full text-xs mt-1")
    with pb:
        mt.button("Ocean",    key="btn_ocean",    class_="w-full text-xs")
        mt.button("Forest",   key="btn_forest",   class_="w-full text-xs mt-1")

    mt.markdown("---")
    mt.write("class_ targets the primary HTML element of each component.",
             class_="text-xs text-slate-400")

# ── PAGE HEADER ────────────────────────────────────────────────────────────────
mt.title("mxlit Kitchen Sink", class_="text-3xl font-extrabold")
mt.write(
    "Every component · every layout · all themed via constants/theme.json. "
    "Adjust colours in the sidebar — the page updates live.",
    class_="max-w-2xl",
)

# ── MATERIAL TOKEN SWATCHES ────────────────────────────────────────────────────
mt.subheader("Material Design Token Palette", class_="mt-6 mb-2")
_swatches = [
    (p,     p_on,  "Primary",          "schemes.light.primary"),
    (p_ctr, txt,   "PrimaryContainer", "schemes.light.primaryContainer"),
    (s,     "#FFF","Secondary",        "schemes.light.secondary"),
    (s_ctr, txt,   "SecContainer",     "schemes.light.secondaryContainer"),
    (tert,  "#FFF","Tertiary",         "schemes.light.tertiary"),
    (t_ctr, txt,   "TertContainer",    "schemes.light.tertiaryContainer"),
    (err,   "#FFF","Error",            "schemes.light.error"),
    (surf,  txt,   "SurfaceVariant",   "schemes.light.surfaceVariant"),
]
_sw = '<div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
for _col, _on, _name, _key in _swatches:
    _sw += (
        f'<div style="text-align:center;" title="{_key}">'
        f'<div style="width:64px;height:64px;border-radius:0.5rem;'
        f'background:{_col};border:1px solid {outl}33;"></div>'
        f'<span style="font-size:0.58rem;font-family:monospace;color:{_on};'
        f'background:{_col};display:block;margin-top:3px;border-radius:0 0 0.5rem 0.5rem;">'
        f'{_name}<br>{_col}</span></div>'
    )
_sw += "</div>"
mt.html(_sw)
mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 1 · TYPOGRAPHY
# ═════════════════════════════════════════════════════════════════════════════
mt.header("1 · Typography", class_="font-bold border-b pb-1")
ta, tb = mt.columns(2)
with ta:
    mt.subheader("Heading sizes")
    mt.title("Title — h1",         class_="text-4xl")
    mt.header("Header — h2",       class_="tracking-widest text-sm uppercase")
    mt.subheader("Subheader — h3", class_="italic font-light")
with tb:
    mt.subheader("Body variants")
    mt.write("Default body text — no class_")
    mt.write("Muted helper text",  class_="text-sm text-slate-400 italic")
    mt.write("Bold CTA",           class_="font-bold")
    mt.write("Mono note",          class_="font-mono text-xs bg-slate-100 px-2 py-0.5 rounded")
    mt.text("mt.text() — fixed-width paragraph")

mt.subheader("Badges")
mt.badge("stable",     class_="bg-green-100  text-green-800  font-semibold")
mt.badge("beta",       class_="bg-yellow-100 text-yellow-800")
mt.badge("deprecated", class_="bg-red-100    text-red-700    line-through")
mt.badge("new",        class_="bg-blue-100   text-blue-800   font-bold")

mt.subheader("Code, Markdown, LaTeX")
mt.code('mt.theme({"schemes.light.primary": "#9333ea"})', class_="max-w-xl")
mt.markdown("**Bold**, *italic*, `inline code`, and [links](/) via `mt.markdown()`.")
mt.latex(r"\hat{y} = \sigma\!\left(\mathbf{w}^\top \mathbf{x} + b\right)")
mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 2 · STATUS
# ═════════════════════════════════════════════════════════════════════════════
mt.header("2 · Status", class_="font-bold border-b pb-1")
mt.info("mt.info() — informational banner.")
mt.success("mt.success() — operation succeeded.")
mt.warning("mt.warning() — something needs attention.")
mt.error("mt.error() — action failed or is blocked.")
mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 3 · WIDGETS
# ═════════════════════════════════════════════════════════════════════════════
mt.header("3 · Widgets", class_="font-bold border-b pb-1")
mt.subheader("Buttons")
col1, col2, col3 = mt.columns(3)
with col1:
    mt.write("Full-width", class_="text-xs text-slate-400")
    if mt.button("Save changes", class_="w-full"):
        mt.success("Saved!", class_="mt-1")
with col2:
    mt.write("Fixed width", class_="text-xs text-slate-400")
    mt.button("Cancel", class_="w-28")
with col3:
    mt.write("Default (no class_)", class_="text-xs text-slate-400")
    mt.button("Default")

mt.subheader("Text inputs")
col4, col5 = mt.columns(2)
with col4:
    mt.text_input("Full name",   class_="max-w-sm")
    mt.number_input("Quantity",  min_value=0, max_value=999, value=1,  class_="max-w-xs")
    mt.date_input("Deadline",    class_="max-w-xs")
    mt.slider("Budget ($)", 0, 5000, 1000, class_="max-w-md")
with col5:
    mt.text_area("Notes",        class_="max-w-sm")
    mt.selectbox("Language", ["Python", "Rust", "Go", "TypeScript"], class_="max-w-xs")

mt.subheader("Toggles, checkboxes, radio")
col6, col7 = mt.columns(2)
with col6:
    mt.toggle("Enable notifications", class_="mt-2")
    mt.toggle("Dark mode",            class_="mt-1")
    mt.checkbox("Accept terms",       class_="mt-2")
    mt.checkbox("Subscribe",          class_="mt-1")
with col7:
    mt.radio("Plan", ["Free", "Pro", "Enterprise"], class_="mt-2")
mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 4 · DATA
# ═════════════════════════════════════════════════════════════════════════════
mt.header("4 · Data", class_="font-bold border-b pb-1")

mt.subheader("Metric cards")
m1, m2, m3, m4 = mt.columns(4)
with m1: mt.metric("Revenue",  "$84,200", "+12%",  class_="w-full")
with m2: mt.metric("Users",    "3,412",   "+5%",   class_="w-full")
with m3: mt.metric("Churn",    "1.8%",    "-0.3%", class_="w-full")
with m4: mt.metric("Uptime",   "99.97%",  "Good",  class_="w-full")

mt.subheader("Dataframe & Table")
df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Widget C", "Widget D"],
    "Units":   [120, 84, 210, 47],
    "Revenue": ["$6,000", "$4,200", "$10,500", "$2,350"],
    "Status":  ["Active", "Active", "Active", "Discontinued"],
})
dt1, dt2 = mt.columns(2)
with dt1:
    mt.write("Interactive (mt.dataframe)", class_="text-xs text-slate-400 mb-1")
    mt.dataframe(df, class_="w-full")
with dt2:
    mt.write("Static (mt.table)", class_="text-xs text-slate-400 mb-1")
    mt.table(df, class_="w-full")

mt.subheader("JSON viewer")
mt.json({"token": "schemes.light.primary", "value": p, "alias": "theme_schemes_light_primary"})
mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 5 · CHARTS
# ═════════════════════════════════════════════════════════════════════════════
mt.header("5 · Charts", class_="font-bold border-b pb-1")
cc1, cc2 = mt.columns(2)
with cc1:
    mt.write("Line — monthly active users",
             class_="text-xs font-semibold uppercase tracking-wide")
    mt.line_chart([210, 340, 290, 510, 430, 620, 580],
                  class_="rounded-lg border p-2")
    mt.write("Area — cumulative revenue",
             class_="text-xs font-semibold uppercase tracking-wide mt-4")
    mt.area_chart([12, 19, 28, 41, 53, 68, 90],
                  class_="rounded-lg border p-2")
with cc2:
    mt.write("Bar — revenue by channel",
             class_="text-xs font-semibold uppercase tracking-wide")
    mt.bar_chart({"Direct": 42, "Organic": 28, "Referral": 18, "Paid": 12},
                 class_="rounded-lg border p-2")
    mt.write("Scatter — spend vs conversion",
             class_="text-xs font-semibold uppercase tracking-wide mt-4")
    mt.scatter_chart(
        {"x": [10, 20, 30, 40, 50, 60], "y": [1.2, 2.5, 2.1, 3.8, 3.2, 4.9]},
        class_="rounded-lg border p-2",
    )
mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 6 · LAYOUT
# ═════════════════════════════════════════════════════════════════════════════
mt.header("6 · Layout", class_="font-bold border-b pb-1")

mt.subheader("Tabs")
tab_overview, tab_code, tab_raw = mt.tabs(["Overview", "Code", "Raw JSON"])
with tab_overview:
    mt.write("Tabs partition content without a page reload — full HTMX-driven.")
    mt.metric("Primary token", p, "schemes.light.primary")
with tab_code:
    mt.code(
        'mt.theme({"schemes.light.primary": "#9333ea"})\n'
        'mt.theme({"schemes.light.secondary": "#0d9488"})',
        class_="text-xs",
    )
with tab_raw:
    mt.json({"primary": p, "secondary": s, "background": bg, "onBackground": txt})

mt.subheader("Styled expanders")
with mt.expander("Model details", class_="border rounded-lg"):
    mt.write("Model: **GPT-4o-mini** · Context: 128k · Output: 16k",
             class_="text-sm")
with mt.expander("Raw API response", class_="border rounded-lg mt-2"):
    mt.code('{"id": "chatcmpl-abc123", "object": "chat.completion"}',
            class_="text-xs")

mt.subheader("Horizontal container — tech-stack pills")
with mt.container(horizontal=True,
                  class_="gap-3 flex-wrap p-4 bg-slate-50 rounded-xl border mt-2"):
    mt.badge("Python 3.12",   class_="bg-blue-100   text-blue-800   text-sm px-3 py-1")
    mt.badge("FastAPI 0.111", class_="bg-green-100  text-green-800  text-sm px-3 py-1")
    mt.badge("Tailwind v4",   class_="bg-sky-100    text-sky-800    text-sm px-3 py-1")
    mt.badge("oat.ink",       class_="bg-purple-100 text-purple-800 text-sm px-3 py-1")
    mt.badge("HTMX 2.x",     class_="bg-orange-100 text-orange-800 text-sm px-3 py-1")

mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 7 · ADVANCED
# ═════════════════════════════════════════════════════════════════════════════
mt.header("7 · Advanced", class_="font-bold border-b pb-1")

mt.subheader("Named-entity recognition")
mt.ner_text(
    "Tesla opened a Gigafactory in Austin, Texas — a project backed by Elon Musk.",
    entities=[
        {"start": 0,  "end": 5,  "label": "ORG"},
        {"start": 16, "end": 27, "label": "FAC"},
        {"start": 31, "end": 43, "label": "GPE"},
        {"start": 69, "end": 78, "label": "PERSON"},
    ],
    class_="mt-4 mb-6 text-base leading-loose",
)

mt.subheader("Streaming text")
def _stream_demo():
    words = ("mxlit streams tokens live via HTMX — "
             "no WebSocket, no polling, just server-sent events.").split()
    import time
    for w in words:
        yield w + " "
        time.sleep(0.07)

mt.write_stream(_stream_demo())

mt.markdown("---")
mt.write(
    "All styles were applied via class_ — no custom CSS written. "
    "Theme tokens are sourced from constants/theme.json (schemes.light.*). "
    "Change the palette in the sidebar to see every component update live.",
    class_="text-center text-sm pb-8",
)
