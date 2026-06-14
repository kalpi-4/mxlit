"""
demo_new_features.py — showcase of every widget and OAT component added beyond
the original Streamlit baseline.

Run with:
    mxlit run samples/demo_new_features.py
"""
import mxlit as mt

mt.title("mxlit — New Features Demo")
mt.write("Showcases every component added beyond the Streamlit baseline.")
mt.breadcrumb([{"label": "Demos"}, {"label": "New Features"}])
mt.markdown("---")

# ── 1. Text extras ────────────────────────────────────────────────────────────
mt.header("1 · Text Extras")

mt.subheader("LaTeX")
mt.latex(r"E = mc^2")
mt.latex(r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")

mt.subheader("Badge")
for label in ["new", "beta", "v2.0", "stable"]:
    mt.badge(label)

mt.markdown("---")

# ── 2. Media ─────────────────────────────────────────────────────────────────
mt.header("2 · Media")
mt.logo("https://picsum.photos/seed/logo/160/48")
mt.write("Audio:")
mt.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
mt.write("Video:")
mt.video("https://www.w3schools.com/html/mov_bbb.mp4")

mt.markdown("---")

# ── 3. Input widgets ──────────────────────────────────────────────────────────
mt.header("3 · Input Widgets")

c1, c2 = mt.columns(2)
with c1:
    num = mt.number_input("Select a number", min_value=0, max_value=100, value=42)
    mt.write(f"Number: {num}")

    color = mt.color_picker("Pick a color", value="#4f46e5")
    mt.write(f"Color: {color}")

    date = mt.date_input("Select a date", value="2024-01-01")
    mt.write(f"Date: {date}")

    is_toggled = mt.toggle("Enable advanced settings", value=True)
    mt.write(f"Toggled: {is_toggled}")

with c2:
    text_area_val = mt.text_area("Tell us about yourself", value="I love coding in Python!")
    mt.write(f"Length: {len(text_area_val)} chars")

    radio_val = mt.radio("Framework", options=["FastAPI", "Mxlit", "Flask"], index=1)
    mt.write(f"Radio: {radio_val}")

    select_val = mt.selectbox("Language", options=["Python", "JavaScript", "Rust", "Go"])
    mt.write(f"Select: {select_val}")

mt.markdown("---")

# ── 4. New form input types ───────────────────────────────────────────────────
mt.header("4 · New Form Input Types")

ni1, ni2 = mt.columns(2)
with ni1:
    mt.email_input("Work email", value="alice@example.com", key="nf_email")
    mt.password_input("Password", key="nf_pwd")
    mt.datetime_input("Appointment", key="nf_dt")
with ni2:
    mt.time_input("Start time", value="09:00", key="nf_time")
    fname = mt.file_input("Attach file", accept=".pdf,.csv,.png", key="nf_file")
    if fname:
        mt.success(f"Uploaded: **{fname}**")
    else:
        mt.info("No file selected.")

mt.markdown("---")

# ── 5. Selection widgets ──────────────────────────────────────────────────────
mt.header("5 · Selection Widgets")

sw1, sw2 = mt.columns(2)
with sw1:
    tags = mt.multiselect(
        "Tags", ["web", "api", "data", "ml", "ui"],
        default=["web", "api"], key="nf_tags",
    )
    mt.write(f"Tags: {tags}")

    speed = mt.select_slider(
        "Speed", options=["slow", "medium", "fast", "ludicrous"],
        value="medium", key="nf_speed",
    )
    mt.write(f"Speed: {speed}")

with sw2:
    view = mt.pills("View mode", ["List", "Grid", "Table"], key="nf_view")
    mt.write(f"View: {view}")

    mt.write("Feedback widgets:")
    thumbs = mt.feedback("Was this helpful?", sentiment="thumbs", key="nf_thumbs")
    if thumbs:
        mt.write(f"Vote: {thumbs}")
    stars = mt.feedback("Rate this page", sentiment="stars", key="nf_stars")
    if stars:
        mt.write(f"Stars: {stars}/5")

mt.markdown("---")

# ── 6. Action widgets ─────────────────────────────────────────────────────────
mt.header("6 · Action Widgets")

mt.link_button("Visit oat.ink", url="https://oat.ink", new_tab=True)

_csv = "name,score\nAlice,95\nBob,87\nCarol,92\n"
mt.download_button("Download scores.csv", data=_csv, file_name="scores.csv", mime="text/csv")

mt.markdown("---")

# ── 7. Charts ─────────────────────────────────────────────────────────────────
mt.header("7 · Charts")

_data = {"Jan": 12000, "Feb": 15400, "Mar": 11800, "Apr": 18200, "May": 21000, "Jun": 19500}

ch1, ch2 = mt.columns(2)
with ch1:
    mt.write("**Line chart**")
    mt.line_chart(_data, title="Monthly Revenue")
    mt.write("**Area chart**")
    mt.area_chart(_data, title="Monthly Revenue")
with ch2:
    mt.write("**Bar chart**")
    mt.bar_chart(_data, title="Monthly Revenue")
    mt.write("**Scatter chart**")
    mt.scatter_chart({"x": [1, 2, 3, 4, 5], "y": [4, 5, 2, 7, 3]}, title="Sample")

mt.markdown("---")

# ── 8. Status messages ────────────────────────────────────────────────────────
mt.header("8 · Status Messages")
mt.success("Operation completed successfully!")
mt.info("This is an informational message.")
mt.warning("Be careful with this action.")
mt.error("Something went wrong.")

try:
    1 / 0
except Exception as e:
    mt.exception(e)

mt.markdown("---")

# ── 9. OAT UI Primitives ──────────────────────────────────────────────────────
mt.header("9 · OAT UI Primitives")

mt.subheader("Spinner & Skeleton")
sp1, sp2, sp3 = mt.columns(3)
with sp1:
    mt.write("large spinner", className="text-xs font-semibold")
    mt.spinner("large")
with sp2:
    mt.write("small spinner", className="text-xs font-semibold")
    mt.spinner("small")
with sp3:
    mt.write("skeleton", className="text-xs font-semibold")
    mt.skeleton("line")
    mt.skeleton("line")
    mt.skeleton("box")

mt.subheader("Progress & Meter")
pr1, pr2 = mt.columns(2)
with pr1:
    mt.write("30 %")
    mt.progress(0.30)
    mt.write("100 %")
    mt.progress(1.0)
    mt.write("Indeterminate:")
    mt.progress()
with pr2:
    mt.write("Meter — optimal (0.55):")
    mt.meter(0.55, low=0.3, high=0.7, optimum=0.5)
    mt.write("Meter — low (0.15):")
    mt.meter(0.15, low=0.3, high=0.7, optimum=1.0)

mt.subheader("Avatar & Avatar Group")
av1, av2 = mt.columns(2)
with av1:
    mt.avatar(initials="JD", size="large")
    mt.avatar(initials="AB")
    mt.avatar(initials="MK", size="small")
with av2:
    mt.avatar_group(avatars=[
        {"initials": "JD"},
        {"initials": "AB"},
        {"initials": "MK"},
        {"initials": "RS"},
    ])

mt.subheader("Toast notification")
if mt.button("Fire success toast", key="nf_toast"):
    mt.toast("Saved!", title="Done", variant="success")

mt.markdown("---")

# ── 10. Layout extras ────────────────────────────────────────────────────────
mt.header("10 · Layout Extras")

mt.subheader("Card")
with mt.card("Revenue", footer="Last 30 days"):
    mt.metric("MRR", "$19,500", "+$1,300")
    mt.progress(0.72)

mt.subheader("Status container")
with mt.status("Build pipeline", state="complete"):
    mt.write("✓ Fetch dependencies")
    mt.write("✓ Run tests")
    mt.write("✓ Deploy to staging")

mt.subheader("Dialog")
with mt.dialog("Confirm action", trigger_label="Open dialog"):
    mt.warning("This action cannot be undone.")
    mt.text_input("Type DELETE to confirm", key="nf_dlg_confirm")

mt.subheader("Dropdown")
mt.dropdown("Options", items=[
    {"label": "Edit"},
    {"label": "Duplicate"},
    {"label": "Archive"},
])

mt.subheader("Button group")
mt.button_group(["Day", "Week", "Month"], key_prefix="nf_period_")

mt.subheader("Popover")
with mt.popover("Settings"):
    mt.toggle("Dark mode", key="nf_pop_dark")
    mt.toggle("Compact view", key="nf_pop_compact")

mt.subheader("Pagination")
_page = mt.pagination(total_pages=8, current_page=1, key="nf_page")
mt.write(f"Page **{_page}** of 8")

mt.subheader("Input group")
with mt.input_group(prefix="https://", suffix=".io"):
    mt.text_input("Subdomain", key="nf_subdomain", className="w-full")

mt.subheader("Breadcrumb")
mt.breadcrumb([
    {"label": "Home", "href": "#"},
    {"label": "Demos", "href": "#"},
    {"label": "New Features"},
])
