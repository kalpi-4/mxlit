"""
oat_sample.py — mxlit showcase inspired by https://oat.ink/recipes/

Recipes demonstrated:
  1. Split Button   – joined controls + secondary action dropdown
  2. Form Card      – grouped form fields inside a styled card
  3. Empty State    – centred card for no-content screens
  4. Stats Cards    – dashboard metrics with badge & progress indicators
"""

import mxlit as mt

# ── session state bootstrap ────────────────────────────────────────────────────
_RECIPES = ["Split Button", "Form Card", "Empty State", "Stats Cards", "New Components"]

for key, default in [
    ("save_action", None),
    ("profile_saved", False),
    ("profile_name", "Your name"),
    ("profile_email", "mila@example.com"),
    ("notif_enabled", True),
    ("created_something", False),
    ("active_recipe", "Split Button"),
]:
    if key not in mt.session_state:
        mt.session_state[key] = default

# ── sidebar ────────────────────────────────────────────────────────────────────
with mt.sidebar:
    mt.title("🌾 Oat Recipes")
    mt.write("A mxlit showcase of composable UI patterns from oat.ink/recipes/")
    mt.markdown("---")
    recipe = mt.radio(
        "Choose recipe",
        _RECIPES,
        index=_RECIPES.index(mt.session_state["active_recipe"]),
        key="active_recipe",
    )
    mt.markdown("---")
    mt.write("Built with **mxlit** + [oat.ink](https://oat.ink) CSS")

# ── page title ─────────────────────────────────────────────────────────────────
mt.title("🌾 Oat UI Recipes")
mt.write("Interactive demos of the composable UI patterns from **oat.ink/recipes/**.")
mt.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# Recipe 1 — Split Button
# ══════════════════════════════════════════════════════════════════════════════
if recipe == "Split Button":
    mt.header("Split Button")
    mt.write(
        "Use joined button controls and a dropdown for secondary save actions. "
        "Pick an action from the secondary menu, then hit **Save**."
    )

    with mt.grid():
        with mt.row():
            with mt.col(5):
                save_clicked = mt.button("💾 Save", key="btn_save")
            with mt.col(7):
                action = mt.selectbox(
                    "More save actions",
                    ["Save draft", "Save and publish", "Duplicate"],
                    key="save_action_select",
                )

    if save_clicked:
        mt.session_state["save_action"] = action
        mt.success(f"✅ Action triggered: **{action}**")
    elif mt.session_state["save_action"]:
        mt.success(f"✅ Last action: **{mt.session_state['save_action']}**")
    else:
        mt.info("Select a save mode and click **Save**.")

# ══════════════════════════════════════════════════════════════════════════════
# Recipe 2 — Form Card
# ══════════════════════════════════════════════════════════════════════════════
elif recipe == "Form Card":
    mt.header("Form Card")
    mt.write("Group related form fields inside a card with a header and action footer.")

    with mt.card("Edit Profile", footer="All fields are required"):
        name  = mt.text_input("Name",  value=mt.session_state["profile_name"],  key="profile_name")
        email = mt.email_input("Email", value=mt.session_state["profile_email"], key="profile_email")
        notif = mt.toggle("Email notifications", value=mt.session_state["notif_enabled"], key="notif_enabled")

    with mt.grid():
        with mt.row():
            with mt.col(6):
                cancelled = mt.button("Cancel", key="btn_cancel")
            with mt.col(6):
                saved = mt.button("Save Profile", key="btn_save_profile")

    if saved:
        mt.session_state["profile_saved"] = True
    if cancelled:
        mt.session_state["profile_saved"] = False

    if mt.session_state["profile_saved"]:
        mt.success(
            f"✅ Profile updated — **{name}** ({email}) | "
            f"Notifications: {'on' if notif else 'off'}"
        )

# ══════════════════════════════════════════════════════════════════════════════
# Recipe 3 — Empty State
# ══════════════════════════════════════════════════════════════════════════════
elif recipe == "Empty State":
    mt.header("Empty State")
    mt.write(
        "Use a centred card with a title, muted description, and a primary action "
        "for list or result empty states."
    )

    with mt.card():
        if not mt.session_state["created_something"]:
            mt.info("Nothing here yet — why don't you create something?")
            if mt.button("＋ New something", key="btn_create"):
                mt.session_state["created_something"] = True
                mt.rerun()
        else:
            mt.success("🎉 Something was created! The empty state is gone.")
            with mt.grid():
                with mt.row():
                    with mt.col(6):
                        mt.metric("Items", 1, "+1")
            if mt.button("Reset", key="btn_reset_empty"):
                mt.session_state["created_something"] = False
                mt.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# Recipe 4 — Stats Cards
# ══════════════════════════════════════════════════════════════════════════════
elif recipe == "Stats Cards":
    mt.header("Stats Cards")
    mt.write(
        "Compose dashboard metrics using `mt.card`, `mt.badge`, `mt.metric`, "
        "`mt.progress`, and `mt.meter` — the new approach, no raw HTML."
    )

    with mt.grid():
        with mt.row():
            with mt.col(4):
                with mt.card("Revenue"):
                    mt.badge("+12%")
                    mt.metric("MRR", "$42,200", "+$4,500 vs last month")
                    mt.progress(0.72)
            with mt.col(4):
                with mt.card("Completion"):
                    mt.badge("-2%")
                    mt.metric("Checkout", "4.6%", "conversion rate")
                    mt.meter(0.46, low=0.3, high=0.7, optimum=1.0)
            with mt.col(4):
                with mt.card("Tickets"):
                    mt.badge("14")
                    mt.metric("Queue", "14", "support tickets")
                    mt.progress(0.35)

    mt.markdown("---")
    mt.write(
        "Each stat card uses `mt.card`, `mt.badge`, `mt.metric`, `mt.progress` / "
        "`mt.meter` — all native mxlit components, no `mt.html()` needed."
    )

# ══════════════════════════════════════════════════════════════════════════════
# Recipe 5 — New Components
# ══════════════════════════════════════════════════════════════════════════════
elif recipe == "New Components":
    mt.header("New OAT Components")
    mt.write("All 19 new UI primitives and form variants added in the component gap fill.")

    mt.breadcrumb([
        {"label": "Recipes", "href": "#"},
        {"label": "New Components"},
    ])

    mt.subheader("Spinner · Skeleton")
    with mt.grid():
        with mt.row():
            with mt.col(4):
                mt.write("Large spinner", className="text-xs font-semibold")
                mt.spinner("large")
            with mt.col(4):
                mt.write("Small spinner", className="text-xs font-semibold")
                mt.spinner("small")
            with mt.col(4):
                mt.write("Skeleton placeholders", className="text-xs font-semibold")
                mt.skeleton("line")
                mt.skeleton("line")
                mt.skeleton("box")

    mt.subheader("Avatar · Avatar Group")
    with mt.grid():
        with mt.row():
            with mt.col(6):
                mt.avatar(initials="JD")
                mt.avatar(initials="AB", size="small")
            with mt.col(6):
                mt.avatar_group(avatars=[
                    {"initials": "JD"},
                    {"initials": "AB"},
                    {"initials": "MK"},
                ])

    mt.subheader("Button Group · Dropdown")
    mt.button_group(["List", "Grid", "Table"], key_prefix="view_mode_")
    mt.dropdown("Export", items=[
        {"label": "Export as CSV"},
        {"label": "Export as JSON"},
        {"label": "Export as PDF"},
    ])

    mt.subheader("Dialog · Toast")
    with mt.grid():
        with mt.row():
            with mt.col(6):
                with mt.dialog("Confirm", trigger_label="Open modal"):
                    mt.write("This is a native `<dialog closedby='any'>` element.")
                    mt.info("Click outside or press Escape to dismiss.")
            with mt.col(6):
                if mt.button("Fire toast", key="recipe5_toast"):
                    mt.toast("Action completed!", title="Done", variant="success")

    mt.subheader("Pagination")
    _r5_page = mt.pagination(total_pages=8, current_page=1, key="r5_page")
    mt.write(f"Page **{_r5_page}** of 8 selected")

    mt.subheader("New form inputs")
    with mt.grid():
        with mt.row():
            with mt.col(6):
                mt.email_input("Work email", className="max-w-sm")
                mt.password_input("Password",  className="max-w-sm")
            with mt.col(6):
                mt.datetime_input("Schedule",  className="max-w-sm")
                mt.file_input("Attach file", accept=".pdf,.png", className="max-w-sm")

    mt.subheader("Input group")
    with mt.input_group(prefix="https://", suffix=".io"):
        mt.text_input("Subdomain", className="w-full")
