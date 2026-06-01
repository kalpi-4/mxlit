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
        # Default oat.ink warm neutral — schemes.light defaults
        "schemes.light.primary":   "#574747",   # schemes.light.primary
        "schemes.light.secondary": "#71717A",   # palettes.secondary[50] / schemes.light.outline
    },
    "btn_ocean": {
        # Cool zinc + fresh green — muted but alive
        "schemes.light.primary":   "#57575C",   # palettes.secondary[40]
        "schemes.light.secondary": "#33A05A",   # palettes.tertiary[60]
    },
    "btn_sunset": {
        # Rich warm tones — deep red-brown primary, dusty-rose secondary
        "schemes.light.primary":   "#543636",   # palettes.primary[30]
        "schemes.light.secondary": "#856363",   # palettes.primary[50]
    },
    "btn_forest": {
        # Deep forest green primary, earthy bark secondary
        "schemes.light.primary":   "#006E2D",   # palettes.tertiary[40]
        "schemes.light.secondary": "#543636",   # palettes.primary[30]
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
p_on     = _t["schemes.light.onPrimary"]              # text colour on primary
p_ctr    = _t["schemes.light.primaryContainer"]       # primary tint container
p_ctr_on = _t["schemes.light.onPrimaryContainer"]     # text on primary container
s_on     = _t["schemes.light.onSecondary"]            # text colour on secondary
s_ctr    = _t["schemes.light.secondaryContainer"]     # secondary tint container
s_ctr_on = _t["schemes.light.onSecondaryContainer"]   # text on secondary container
tert     = _t["schemes.light.tertiary"]               # tertiary accent
t_ctr    = _t["schemes.light.tertiaryContainer"]      # tertiary container
t_ctr_on = _t["schemes.light.onTertiaryContainer"]    # text on tertiary container
err      = _t["schemes.light.error"]                  # error / danger
err_ctr  = _t["schemes.light.errorContainer"]         # error container
err_ctr_on = _t["schemes.light.onErrorContainer"]     # text on error container
surf     = _t["schemes.light.surfaceVariant"]         # subtle raised surface
surf_low = _t["schemes.light.surfaceContainerLow"]    # lower surface level
outl     = _t["schemes.light.outline"]                # border / divider colour

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with mt.sidebar:
    mt.title("Theme Generator", class_="text-base font-bold tracking-tight")
    mt.write("Colours sourced from constants/theme.json (schemes.light.*).",
             class_="text-xs mb-3")

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
    mt.html(f'<p style="font-size:0.7rem;color:{outl};">'
            f'class_ targets the primary HTML element of each component.</p>')

    # ── Material Design Token Palette ──────────────────────────────────────────
    mt.markdown("---")
    mt.write("Material Token Palette",
             class_="text-xs font-semibold uppercase tracking-wide mt-1 mb-2")

    mt.html(f'<p style="font-size:0.6rem;font-weight:700;color:{outl};'
            f'letter-spacing:0.06em;text-transform:uppercase;'
            f'border-bottom:1px solid {outl}33;padding-bottom:2px;margin-bottom:4px;">Primary</p>')
    mt.color_picker("primary",            value=p,       key="theme_schemes_light_primary")
    mt.color_picker("onPrimary",          value=p_on,    key="theme_schemes_light_onPrimary")
    mt.color_picker("primaryContainer",   value=p_ctr,   key="theme_schemes_light_primaryContainer")
    mt.color_picker("onPrimaryContainer", value=p_ctr_on, key="theme_schemes_light_onPrimaryContainer")

    mt.html(f'<p style="font-size:0.6rem;font-weight:700;color:{outl};'
            f'letter-spacing:0.06em;text-transform:uppercase;'
            f'border-bottom:1px solid {outl}33;padding-bottom:2px;margin:8px 0 4px;">Secondary</p>')
    mt.color_picker("secondary",              value=s,       key="theme_schemes_light_secondary")
    mt.color_picker("onSecondary",            value=s_on,    key="theme_schemes_light_onSecondary")
    mt.color_picker("secondaryContainer",     value=s_ctr,   key="theme_schemes_light_secondaryContainer")
    mt.color_picker("onSecondaryContainer",   value=s_ctr_on, key="theme_schemes_light_onSecondaryContainer")

    mt.html(f'<p style="font-size:0.6rem;font-weight:700;color:{outl};'
            f'letter-spacing:0.06em;text-transform:uppercase;'
            f'border-bottom:1px solid {outl}33;padding-bottom:2px;margin:8px 0 4px;">Tertiary</p>')
    mt.color_picker("tertiary",            value=tert,    key="theme_schemes_light_tertiary")
    mt.color_picker("tertiaryContainer",   value=t_ctr,   key="theme_schemes_light_tertiaryContainer")
    mt.color_picker("onTertiaryContainer", value=t_ctr_on, key="theme_schemes_light_onTertiaryContainer")

    mt.html(f'<p style="font-size:0.6rem;font-weight:700;color:{outl};'
            f'letter-spacing:0.06em;text-transform:uppercase;'
            f'border-bottom:1px solid {outl}33;padding-bottom:2px;margin:8px 0 4px;">Error</p>')
    mt.color_picker("error",            value=err,      key="theme_schemes_light_error")
    mt.color_picker("errorContainer",   value=err_ctr,  key="theme_schemes_light_errorContainer")
    mt.color_picker("onErrorContainer", value=err_ctr_on, key="theme_schemes_light_onErrorContainer")

    mt.html(f'<p style="font-size:0.6rem;font-weight:700;color:{outl};'
            f'letter-spacing:0.06em;text-transform:uppercase;'
            f'border-bottom:1px solid {outl}33;padding-bottom:2px;margin:8px 0 4px;">Surface / Outline</p>')
    mt.color_picker("background",          value=bg,       key="theme_schemes_light_background")
    mt.color_picker("onBackground",        value=txt,      key="theme_schemes_light_onBackground")
    mt.color_picker("surfaceVariant",      value=surf,     key="theme_schemes_light_surfaceVariant")
    mt.color_picker("surfaceContainerLow", value=surf_low, key="theme_schemes_light_surfaceContainerLow")
    mt.color_picker("outline",             value=outl,     key="theme_schemes_light_outline")

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
    (p,     p_on,     "Primary",          "schemes.light.primary"),
    (p_ctr, p_ctr_on, "PrimaryContainer", "schemes.light.primaryContainer"),
    (s,     s_on,     "Secondary",        "schemes.light.secondary"),
    (s_ctr, s_ctr_on, "SecContainer",     "schemes.light.secondaryContainer"),
    (tert,  p_on,     "Tertiary",         "schemes.light.tertiary"),
    (t_ctr, t_ctr_on, "TertContainer",    "schemes.light.tertiaryContainer"),
    (err,   p_on,     "Error",            "schemes.light.error"),
    (surf,  txt,      "SurfaceVariant",   "schemes.light.surfaceVariant"),
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
    mt.html(f'<p style="font-size:0.875rem;color:{outl};font-style:italic;">Muted helper text</p>')
    mt.write("Bold CTA",           class_="font-bold")
    mt.html(f'<p style="font-family:monospace;font-size:0.75rem;background:{surf};'
            f'padding:0.125rem 0.5rem;border-radius:0.25rem;display:inline-block;">Mono note</p>')
    mt.text("mt.text() — fixed-width paragraph")

mt.subheader("Badges")
# mt.badge() uses OAT's <span class="badge"> — no hardcoded colour needed
_b1, _b2, _b3, _b4 = mt.columns(4)
with _b1: mt.badge("stable")
with _b2: mt.badge("beta")
with _b3: mt.badge("deprecated")
with _b4: mt.badge("new")

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
    mt.html(f'<p style="font-size:0.75rem;color:{outl};">Full-width</p>')
    if mt.button("Save changes", class_="w-full"):
        mt.success("Saved!", class_="mt-1")
with col2:
    mt.html(f'<p style="font-size:0.75rem;color:{outl};">Fixed width</p>')
    mt.button("Cancel", class_="w-28")
with col3:
    mt.html(f'<p style="font-size:0.75rem;color:{outl};">Default (no class_)</p>')
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

mt.subheader("New inputs — email · password · datetime · file")
col8, col9 = mt.columns(2)
with col8:
    mt.email_input("Email address",   class_="max-w-sm")
    mt.password_input("Password",     class_="max-w-sm")
with col9:
    mt.datetime_input("Appointment",  class_="max-w-sm")
    mt.file_input("Upload document",  accept=".pdf,.docx", class_="max-w-sm")

mt.subheader("Input group — prefix / suffix")
with mt.input_group(prefix="https://", suffix=".com"):
    mt.text_input("Domain", class_="w-full")
mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 4 · DATA
# ═════════════════════════════════════════════════════════════════════════════
mt.header("4 · Data", class_="font-bold border-b pb-1")

mt.subheader("Metric cards — wrapped in mt.card()")
with mt.card("Dashboard Overview"):
    m1, m2, m3, m4 = mt.columns(4)
    with m1: mt.metric("Revenue", "$84,200", "+12%")
    with m2: mt.metric("Users",   "3,412",   "+5%")
    with m3: mt.metric("Churn",   "1.8%",    "-0.3%")
    with m4: mt.metric("Uptime",  "99.97%",  "Good")

mt.subheader("Dataframe & Table")
df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Widget C", "Widget D"],
    "Units":   [120, 84, 210, 47],
    "Revenue": ["$6,000", "$4,200", "$10,500", "$2,350"],
    "Status":  ["Active", "Active", "Active", "Discontinued"],
})
dt1, dt2 = mt.columns(2)
with dt1:
    mt.html(f'<p style="font-size:0.75rem;color:{outl};margin-bottom:0.25rem;">Interactive (mt.dataframe)</p>')
    mt.dataframe(df, class_="w-full")
with dt2:
    mt.html(f'<p style="font-size:0.75rem;color:{outl};margin-bottom:0.25rem;">Static (mt.table)</p>')
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

mt.subheader("Tech-stack badges — mt.badge() instead of raw HTML")
for _lbl in ["Python 3.12", "FastAPI 0.111", "Tailwind v4", "oat.ink", "HTMX 2.x"]:
    mt.badge(_lbl)

mt.subheader("Breadcrumb navigation")
mt.breadcrumb([
    {"label": "Home",       "href": "/"},
    {"label": "Components", "href": "/components"},
    {"label": "Layout"},
])

mt.subheader("Button group — segmented control")
mt.button_group(["Day", "Week", "Month", "Year"], key_prefix="time_")

mt.subheader("Dropdown menu")
mt.dropdown("Actions", items=[
    {"label": "Edit",      "href": "#"},
    {"label": "Duplicate"},
    {"label": "Delete"},
])

mt.subheader("Modal dialog")
with mt.dialog("Confirm Action", trigger_label="Open Dialog"):
    mt.write("Are you sure you want to proceed with this action?")
    mt.info("This action cannot be undone.")

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

mt.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 8 · NEW UI PRIMITIVES
# ═════════════════════════════════════════════════════════════════════════════
mt.header("8 · New UI Primitives", class_="font-bold border-b pb-1")

mt.subheader("Spinner & Skeleton")
sp1, sp2, sp3 = mt.columns(3)
with sp1:
    mt.write("Spinner — large", class_="text-xs font-semibold")
    mt.spinner("large")
with sp2:
    mt.write("Spinner — small", class_="text-xs font-semibold")
    mt.spinner("small")
with sp3:
    mt.write("Skeleton placeholders", class_="text-xs font-semibold")
    mt.skeleton("line")
    mt.skeleton("line")
    mt.skeleton("box")

mt.subheader("Progress & Meter")
pr1, pr2 = mt.columns(2)
with pr1:
    mt.write("Progress bar (72 %)", class_="text-xs")
    mt.progress(0.72)
    mt.write("Indeterminate", class_="text-xs mt-2")
    mt.progress()
with pr2:
    mt.write("Meter — green zone (0.75)", class_="text-xs")
    mt.meter(0.75, low=0.3, high=0.7, optimum=1.0)
    mt.write("Meter — warning zone (0.45)", class_="text-xs mt-2")
    mt.meter(0.45, low=0.3, high=0.7, optimum=1.0)

mt.subheader("Avatar & Avatar Group")
av1, av2 = mt.columns(2)
with av1:
    mt.write("Single avatar — initials", class_="text-xs font-semibold")
    mt.avatar(initials="JD")
    mt.write("Small avatar", class_="text-xs mt-2")
    mt.avatar(initials="AB", size="small")
with av2:
    mt.write("Avatar group", class_="text-xs font-semibold")
    mt.avatar_group(avatars=[
        {"initials": "JD"},
        {"initials": "AB"},
        {"initials": "MK"},
    ])

mt.subheader("Pagination")
_page = mt.pagination(total_pages=5, current_page=1, key="demo_page")
mt.write(f"Selected page: **{_page}**")

mt.subheader("Toast notification")
mt.write("Click the button to fire a toast:", class_="text-sm")
if mt.button("Show success toast", key="demo_toast"):
    mt.toast("Changes saved successfully!", title="Saved", variant="success")

mt.markdown("---")
mt.write(
    "All components use OAT semantic attributes — no hardcoded Tailwind colour classes. "
    "Theme tokens from constants/theme.json (schemes.light.*). "
    "Edit colours in the sidebar to see every element update live.",
    class_="text-center text-sm pb-8",
)
