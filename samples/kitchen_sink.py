"""
kitchen_sink.py — every mxlit component in one file.

Browse the full API across seven sections via the sidebar radio selector.

Run with:
    mxlit run samples/kitchen_sink.py
"""

import math
import random

import mxlit as mt
import pandas as pd

# ── session bootstrap ──────────────────────────────────────────────────────────
_SECTIONS = [
    "Typography",
    "Widgets",
    "Actions",
    "Data & Charts",
    "Layout",
    "OAT Extras",
    "Status & Alerts",
]

for _k, _v in [
    ("ks_section",    "Typography"),
    ("ks_btn_clicks", 0),
]:
    if _k not in mt.session_state:
        mt.session_state[_k] = _v

# ── sidebar ────────────────────────────────────────────────────────────────────
with mt.sidebar:
    mt.title("Kitchen Sink")
    mt.write("Every mxlit component in one place.")
    mt.markdown("---")
    section = mt.radio("Section", _SECTIONS, key="ks_section")
    mt.markdown("---")
    mt.badge("mxlit")
    mt.write("FastAPI · HTMX · oat.ink")

# ── page header ────────────────────────────────────────────────────────────────
mt.title("mxlit Kitchen Sink")
mt.write("Use the sidebar to jump between component sections.")
mt.breadcrumb([{"label": "Kitchen Sink"}, {"label": section}])
mt.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# 1. Typography
# ══════════════════════════════════════════════════════════════════════════════
if section == "Typography":
    mt.header("Typography")

    mt.subheader("Headings")
    mt.title("mt.title — page-level heading")
    mt.header("mt.header — section heading")
    mt.subheader("mt.subheader — sub-section heading")

    mt.subheader("Body text")
    mt.write("mt.write accepts **markdown**, `inline code`, _italics_, and multiple args:", 42, True)
    mt.text("mt.text renders plain, unstyled text.")
    mt.markdown(
        "## mt.markdown\n\nFull **Markdown** including tables:\n\n"
        "| Feature | Support |\n|---|---|\n| Tables | ✅ |\n| Fenced code | ✅ |\n| KaTeX | ✅ |"
    )

    mt.subheader("Code block")
    mt.code(
        "import mxlit as mt\n\n"
        "@mt.cache_data\n"
        "def load_data(path: str):\n"
        "    return pd.read_csv(path)\n"
    )

    mt.subheader("Raw HTML")
    mt.html("<strong>mt.html</strong> renders <em>arbitrary HTML</em> — use sparingly.")

    mt.subheader("LaTeX")
    mt.latex(r"E = mc^2 \quad \text{and} \quad \nabla \cdot \mathbf{B} = 0")

    mt.subheader("Badge")
    c1, c2, c3, c4 = mt.columns(4)
    with c1:
        mt.badge("default")
    with c2:
        mt.badge("v1.0.0")
    with c3:
        mt.badge("+12%")
    with c4:
        mt.badge("beta")

    mt.subheader("Named Entity Recognition")
    _ner_text = (
        "Apple is looking at buying U.K. startup for $1 billion. "
        "Tim Cook announced it in San Francisco."
    )
    mt.ner_text(_ner_text, [
        {"start": 0,  "end": 5,  "label": "ORG"},
        {"start": 27, "end": 31, "label": "GPE"},
        {"start": 44, "end": 54, "label": "MONEY"},
        {"start": 56, "end": 64, "label": "PERSON"},
        {"start": 83, "end": 96, "label": "GPE"},
    ])

    mt.subheader("Streaming text")
    mt.write_stream(w + " " for w in "mt.write_stream yields tokens one by one from a generator.".split())


# ══════════════════════════════════════════════════════════════════════════════
# 2. Widgets
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Widgets":
    mt.header("Widgets")

    # Text inputs
    mt.subheader("Text & credential inputs")
    ti1, ti2 = mt.columns(2)
    with ti1:
        name  = mt.text_input("Name",     value="Alice",              key="ks_name")
        email = mt.email_input("Email",   value="alice@example.com",  key="ks_email")
        pwd   = mt.password_input("Password",                         key="ks_pwd")
    with ti2:
        dt    = mt.datetime_input("Appointment",                      key="ks_dt")
        d     = mt.date_input("Date",                                 key="ks_date")
        t     = mt.time_input("Time",     value="09:00",              key="ks_time")
    mt.write(f"name={name!r}  email={email!r}  dt={dt!r}  date={d!r}  time={t!r}")

    mt.subheader("Text area")
    bio = mt.text_area("Bio", value="Tell us about yourself…", key="ks_bio")
    mt.write(f"Character count: **{len(bio)}**")

    # Numeric
    mt.subheader("Numeric inputs")
    ni1, ni2 = mt.columns(2)
    with ni1:
        num    = mt.number_input("Integer (0–100)", min_value=0, max_value=100, value=42, key="ks_num")
        sl_val = mt.slider("Slider (0–100)", 0, 100, value=50, key="ks_slider")
    with ni2:
        speed = mt.select_slider(
            "Speed", options=["slow", "medium", "fast", "ludicrous"],
            value="medium", key="ks_speed",
        )
        color = mt.color_picker("Accent color", value="#4f46e5", key="ks_color")
    mt.write(f"number={num}  slider={sl_val}  speed={speed!r}  color={color!r}")

    # Selection
    mt.subheader("Selection widgets")
    si1, si2 = mt.columns(2)
    with si1:
        lang = mt.selectbox("Language", ["Python", "JavaScript", "Rust", "Go"], key="ks_lang")
        fw   = mt.radio("Framework", ["FastAPI", "Django", "Flask"], key="ks_fw")
    with si2:
        tags = mt.multiselect("Tags", ["web", "api", "data", "ml", "ui"],
                              default=["web", "api"], key="ks_tags")
        view = mt.pills("View mode", ["List", "Grid", "Table"], key="ks_view")
    mt.write(f"lang={lang!r}  fw={fw!r}  tags={tags}  view={view!r}")

    # Booleans
    mt.subheader("Boolean widgets")
    bi1, bi2 = mt.columns(2)
    with bi1:
        dark  = mt.checkbox("Dark mode",      key="ks_dark")
        notif = mt.toggle("Notifications", value=True, key="ks_notif")
    with bi2:
        mt.write(f"dark={dark}  notifications={notif}")

    # File upload
    mt.subheader("File upload")
    fname = mt.file_input("Attach file", accept=".pdf,.csv,.png", key="ks_file")
    if fname:
        mt.success(f"Uploaded: **{fname}**")
    else:
        mt.info("No file selected yet.")

    # Feedback
    mt.subheader("Feedback")
    fb1, fb2 = mt.columns(2)
    with fb1:
        thumbs = mt.feedback("Was this helpful?", sentiment="thumbs", key="ks_thumbs")
        if thumbs:
            mt.write(f"Vote: {thumbs}")
    with fb2:
        stars = mt.feedback("Rate this page", sentiment="stars", key="ks_stars")
        if stars:
            mt.write(f"Stars: {stars} / 5")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Actions
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Actions":
    mt.header("Actions")

    mt.subheader("Button")
    ac1, ac2 = mt.columns([1, 3])
    with ac1:
        if mt.button("Click me", key="ks_btn"):
            mt.session_state["ks_btn_clicks"] += 1
    with ac2:
        mt.write(f"Clicked **{mt.session_state['ks_btn_clicks']}** time(s).")

    mt.button("Disabled", disabled=True, key="ks_btn_dis")

    mt.subheader("Link button")
    mt.link_button("Open oat.ink docs", url="https://oat.ink", new_tab=True)

    mt.subheader("Download button")
    _csv = "name,score\nAlice,95\nBob,87\nCarol,92\n"
    mt.download_button("Download scores.csv", data=_csv, file_name="scores.csv", mime="text/csv")

    mt.subheader("Button group (segmented control)")
    mt.button_group(["List", "Grid", "Table"], key_prefix="ks_mode_")
    _mode = next(
        (lbl for lbl in ["List", "Grid", "Table"]
         if mt.session_state.get(f"ks_mode_{lbl}") == "true"),
        "none selected",
    )
    mt.write(f"Active mode: **{_mode}**")

    mt.subheader("Pagination")
    _page = mt.pagination(total_pages=10, current_page=1, key="ks_page")
    mt.write(f"Current page: **{_page}** of 10")

    mt.subheader("Toast notifications")
    tc1, tc2, tc3 = mt.columns(3)
    with tc1:
        if mt.button("Success toast", key="ks_toast_ok"):
            mt.toast("Saved successfully!", title="Done", variant="success")
    with tc2:
        if mt.button("Warning toast", key="ks_toast_warn"):
            mt.toast("Proceed with caution.", title="Warning", variant="warning")
    with tc3:
        if mt.button("Danger toast", key="ks_toast_err"):
            mt.toast("Something went wrong.", title="Error", variant="danger")


# ══════════════════════════════════════════════════════════════════════════════
# 4. Data & Charts
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Data & Charts":
    mt.header("Data & Charts")

    _df = pd.DataFrame({
        "Month":   ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Revenue": [12000, 15400, 11800, 18200, 21000, 19500],
        "Costs":   [8000,  9100,  8500,  10200, 12000, 11500],
    })
    _rev_by_month = dict(zip(_df["Month"], _df["Revenue"]))

    mt.subheader("Dataframe")
    mt.dataframe(_df)

    mt.subheader("Table")
    mt.table(_df.head(3))

    mt.subheader("JSON")
    mt.json({"framework": "mxlit", "version": "0.1", "features": ["SSE", "HTMX", "OAT"]})

    mt.subheader("Metrics")
    mc1, mc2, mc3 = mt.columns(3)
    with mc1:
        mt.metric("Revenue", "$19,500", "+$1,300")
    with mc2:
        mt.metric("Costs", "$11,500", "-$500")
    with mc3:
        mt.metric("Margin", "41%", "+3 pp")

    mt.subheader("Charts")
    ch1, ch2 = mt.columns(2)
    with ch1:
        mt.write("**Line chart**")
        mt.line_chart(_rev_by_month, title="Monthly Revenue")
    with ch2:
        mt.write("**Bar chart**")
        mt.bar_chart(_rev_by_month, title="Monthly Revenue")

    ch3, ch4 = mt.columns(2)
    with ch3:
        mt.write("**Area chart**")
        mt.area_chart(_rev_by_month, title="Monthly Revenue")
    with ch4:
        mt.write("**Scatter chart**")
        _xs = [i * 0.5 for i in range(12)]
        _ys = [math.sin(x) * 10 + 20 for x in _xs]
        mt.scatter_chart({"x": _xs, "y": _ys}, title="Sine wave")

    mt.subheader("Auto-refresh (setInterval)")
    mt.write("The chart below re-fetches itself every 5 seconds:")
    _live = {m: random.randint(10_000, 25_000) for m in _df["Month"]}
    with mt.setInterval(sync_time=5):
        mt.line_chart(_live, id="ks_live_chart", title="Live Revenue")

    mt.subheader("setTimeout (one-shot refresh)")
    mt.write("The block below re-fetches once 3 s after the page loads:")
    with mt.setTimeout(delay=3):
        mt.info(f"Timestamp snapshot: revenue = {_live}", id="ks_timeout_metric")


# ══════════════════════════════════════════════════════════════════════════════
# 5. Layout
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Layout":
    mt.header("Layout")

    mt.subheader("Columns — equal split")
    la, lb, lc = mt.columns(3)
    with la:
        mt.info("Column 1")
    with lb:
        mt.info("Column 2")
    with lc:
        mt.info("Column 3")

    mt.subheader("Columns — weighted 1:2:1")
    wa, wb, wc = mt.columns([1, 2, 1])
    with wa:
        mt.write("1 part")
    with wb:
        mt.write("2 parts (double width)")
    with wc:
        mt.write("1 part")

    mt.subheader("Container")
    with mt.container(class_="rounded-lg border p-4"):
        mt.write("Content inside `mt.container` with a custom CSS class.")
        mt.badge("contained")

    mt.subheader("Expander")
    with mt.expander("Click to expand"):
        mt.write("Hidden content is revealed on click.")
        mt.code("print('hello from expander')")

    mt.subheader("Card")
    cc1, cc2 = mt.columns(2)
    with cc1:
        with mt.card("Revenue"):
            mt.metric("MRR", "$19,500", "+$1,300")
            mt.progress(0.72)
    with cc2:
        with mt.card("Queue", footer="Last updated: just now"):
            mt.metric("Tickets", "14", "open")
            mt.progress(0.35)

    mt.subheader("Nested tabs")
    nt_a, nt_b = mt.tabs(["Tab A", "Tab B"])
    with nt_a:
        mt.success("Inside nested Tab A")
    with nt_b:
        mt.code("mt.tabs(['Tab A', 'Tab B'])")

    mt.subheader("Grid (12-column)")
    with mt.grid():
        mt.write("Children inside `mt.grid()` are wrapped in the OAT grid container.")

    mt.subheader("Input group")
    with mt.input_group(prefix="https://", suffix=".io"):
        mt.text_input("Subdomain", key="ks_subdomain", class_="w-full")

    mt.subheader("Popover")
    with mt.popover("Settings"):
        mt.toggle("Dark mode",    key="ks_pop_dark")
        mt.toggle("Compact view", key="ks_pop_compact")

    mt.subheader("Status container")
    with mt.status("Build pipeline", state="complete"):
        mt.write("✓ Fetch dependencies")
        mt.write("✓ Run tests")
        mt.write("✓ Deploy to staging")

    mt.subheader("Dialog")
    with mt.dialog("Confirm deletion", trigger_label="Open dialog"):
        mt.warning("This action cannot be undone.")
        mt.write("Type **DELETE** to confirm.")
        mt.text_input("Confirmation", key="ks_dlg_confirm")

    mt.subheader("Dropdown menu")
    mt.dropdown("Options", items=[
        {"label": "Edit"},
        {"label": "Duplicate"},
        {"label": "Archive"},
        {"label": "Delete"},
    ])

    mt.subheader("Space")
    mt.write("↑ above (default spacing)")
    mt.space(2.0)
    mt.write("↑ 2 rem gap via mt.space(2.0)")

    mt.subheader("Empty placeholder")
    mt.empty()
    mt.write("mt.empty() inserts a structural placeholder div.")


# ══════════════════════════════════════════════════════════════════════════════
# 6. OAT Extras
# ══════════════════════════════════════════════════════════════════════════════
elif section == "OAT Extras":
    mt.header("OAT Extras")

    mt.subheader("Breadcrumb")
    mt.breadcrumb([
        {"label": "Home",     "href": "#"},
        {"label": "Products", "href": "#"},
        {"label": "Detail"},
    ])

    mt.subheader("Avatar")
    av1, av2, av3 = mt.columns(3)
    with av1:
        mt.write("Large")
        mt.avatar(initials="JD", size="large")
    with av2:
        mt.write("Default")
        mt.avatar(initials="AB")
    with av3:
        mt.write("Small")
        mt.avatar(initials="MK", size="small")

    mt.subheader("Avatar group")
    mt.avatar_group(avatars=[
        {"initials": "JD"},
        {"initials": "AB"},
        {"initials": "MK"},
        {"initials": "RS"},
    ])

    mt.subheader("Spinner")
    sp1, sp2 = mt.columns(2)
    with sp1:
        mt.write("small")
        mt.spinner("small")
    with sp2:
        mt.write("large")
        mt.spinner("large")

    mt.subheader("Skeleton placeholders")
    mt.skeleton("line")
    mt.skeleton("line")
    mt.skeleton("box")

    mt.subheader("Progress bar")
    mt.write("30 %")
    mt.progress(0.30)
    mt.write("65 %")
    mt.progress(0.65)
    mt.write("100 %")
    mt.progress(1.0)
    mt.write("Indeterminate (no value):")
    mt.progress()

    mt.subheader("Meter (semantic color cues)")
    mt.write("Below low threshold → yellow:")
    mt.meter(0.15, low=0.3, high=0.7, optimum=1.0)
    mt.write("Within optimal range → green:")
    mt.meter(0.55, low=0.3, high=0.7, optimum=0.5)
    mt.write("Above high threshold → yellow:")
    mt.meter(0.85, low=0.3, high=0.7, optimum=0.5)

    mt.subheader("Media")
    mt.write("Image:")
    mt.image("https://picsum.photos/seed/mxlit/600/200", width=600)
    mt.write("Logo:")
    mt.logo("https://picsum.photos/seed/logo/120/40")


# ══════════════════════════════════════════════════════════════════════════════
# 7. Status & Alerts
# ══════════════════════════════════════════════════════════════════════════════
elif section == "Status & Alerts":
    mt.header("Status & Alerts")

    mt.subheader("Alert banners")
    mt.info("mt.info — informational message for the user.")
    mt.success("mt.success — operation completed successfully.")
    mt.warning("mt.warning — action may have unintended consequences.")
    mt.error("mt.error — something went wrong; action required.")

    mt.subheader("Exception display")
    try:
        _ = 1 / 0
    except ZeroDivisionError as exc:
        mt.exception(exc)

    mt.subheader("Caching helpers")
    mt.code(
        "@mt.cache_data\n"
        "def load_df(path: str):\n"
        "    return pd.read_csv(path)  # only runs once per unique path\n\n"
        "@mt.cache_resource\n"
        "def load_model():\n"
        "    return torch.load('model.pt')  # singleton across re-runs"
    )

    mt.subheader("Rerun & Stop")
    rc1, rc2 = mt.columns(2)
    with rc1:
        if mt.button("Trigger rerun", key="ks_rerun"):
            mt.rerun()
    with rc2:
        mt.write("`mt.stop()` halts script execution at the call site.")

    mt.subheader("App options")
    mt.code(
        "mt.get_option('client.showErrorDetails')   # True\n"
        "mt.set_option('server.maxUploadSize', 50)  # MB"
    )
