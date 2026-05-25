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
        ["Split Button", "Form Card", "Empty State", "Stats Cards"],
        index=["Split Button", "Form Card", "Empty State", "Stats Cards"].index(
            mt.session_state["active_recipe"]
        ),
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

    col_btn, col_menu = mt.columns([2, 3])

    with col_btn:
        save_clicked = mt.button("💾 Save", key="btn_save")

    with col_menu:
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

    name = mt.text_input("Name", value=mt.session_state["profile_name"], key="profile_name")
    email = mt.text_input("Email", value=mt.session_state["profile_email"], key="profile_email")
    notif = mt.toggle("Email notifications", value=mt.session_state["notif_enabled"], key="notif_enabled")

    mt.markdown("---")
    col_cancel, col_save = mt.columns([1, 1])
    with col_cancel:
        cancelled = mt.button("Cancel", key="btn_cancel")
    with col_save:
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

    if not mt.session_state["created_something"]:
        mt.info("Nothing here yet — why don't you create something?")
        if mt.button("＋ New something", key="btn_create"):
            mt.session_state["created_something"] = True
            mt.rerun()
    else:
        mt.success("🎉 Something was created! The empty state is gone.")
        col_l, col_r = mt.columns([1, 1])
        with col_l:
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
        "Compose dashboard metrics using columns, metric, badge, and progress "
        "components — mirroring the grid/card pattern from oat.ink."
    )

    col1, col2, col3 = mt.columns(3)

    with col1:
        mt.subheader("Revenue")
        mt.badge("+12%")
        mt.metric("$42,200", "$42,200", "+$4,500 vs last month")
        mt.html(
            '<progress value="72" max="100" '
            'style="width:100%;accent-color:var(--ot-color-success, #22c55e)"></progress>'
        )

    with col2:
        mt.subheader("Completion")
        mt.badge("-2%")
        mt.metric("4.6 %", "4.6%", "checkout completion")
        mt.html(
            '<meter value="0.46" min="0" max="1" low="0.3" high="0.7" optimum="1" '
            'style="width:100%"></meter>'
        )

    with col3:
        mt.subheader("Tickets")
        mt.badge("14")
        mt.metric("14", "14", "support queue")
        mt.html(
            '<progress value="35" max="100" '
            'style="width:100%;accent-color:var(--ot-color-warning, #f59e0b)"></progress>'
        )

    mt.markdown("---")
    mt.write("Each card uses `mt.subheader`, `mt.badge`, `mt.metric`, and raw `mt.html` "
             "for the `<progress>` / `<meter>` elements — all native Oat ink components.")
