"""
gravatar_profile.py — mxlit showcase inspired by a Gravatar public profile page
(https://gravatar.com/<username>).

Recreates the layout, not any real person's photo or private data:
  - Cover banner + overlapping avatar
  - Name / title / location header block
  - Verified-identity badge row
  - Bio with a "Show more" expander
  - Share / Contact action buttons
  - "Verified Accounts" card listing linked social profiles
"""

import mxlit as mt

for key, default in [("bio_expanded", False)]:
    if key not in mt.session_state:
        mt.session_state[key] = default

PROFILE = {
    "name": "Jordan Avery",
    "title": "Senior Software Engineer — Frontend",
    "company": "Acme Corp",
    "pronouns": "They/Them",
    "location": "Bengaluru, India",
    "bio": (
        "Jordan is a multifaceted professional with a passion for engineering and a keen "
        "eye for street photography. As a skilled web developer, they blend creativity with "
        "technical expertise to craft engaging online experiences. Outside of work, Jordan is "
        "an avid sports enthusiast, embracing both the thrill of competition and the "
        "camaraderie of teamwork."
    ),
}

ACCOUNTS = [
    {"label": "LinkedIn",  "icon": "💼", "url": "https://linkedin.com/in/example"},
    {"label": "GitHub",    "icon": "🐙", "url": "https://github.com/example"},
    {"label": "Instagram", "icon": "📷", "url": "https://instagram.com/example"},
]

# Gravatar's verified-badge / CTA blue, used consistently on buttons + badges below.
GRAVATAR_BLUE       = "bg-blue-600 hover:bg-blue-700 text-white border-blue-600"
GRAVATAR_BLUE_BADGE = "bg-blue-600 text-white"

mt.page_config(
    main_class="max-w-xl mx-auto",
    title=f"{PROFILE['name']} | {PROFILE['title']} — mxlit Gravatar Profile Sample",
    description=PROFILE["bio"][:160].rsplit(" ", 1)[0] + "…",
)

# ── profile card ────────────────────────────────────────────────────────────
with mt.card(className="overflow-hidden p-0"):
    with mt.container(className="h-28 bg-gradient-to-r from-slate-300 via-slate-100 to-slate-400"):
        pass

    with mt.container(className="px-6 -mt-12"):
        mt.avatar(initials="JA", size="large", className="ring-4 ring-white")

    with mt.container(className="px-6 pt-3 pb-6"):
        mt.title(PROFILE["name"])
        mt.write(f"{PROFILE['title']} · {PROFILE['company']}")
        mt.write(f"{PROFILE['pronouns']}  ·  {PROFILE['location']}", className="text-sm opacity-70")

        with mt.container(horizontal=True, className="gap-2 mt-2"):
            mt.badge("✓ Identity verified", className=GRAVATAR_BLUE_BADGE)
            for acct in ACCOUNTS:
                mt.badge(acct["icon"], className=GRAVATAR_BLUE_BADGE)

        mt.space(0.5)

        if mt.session_state["bio_expanded"]:
            mt.write(PROFILE["bio"])
            if mt.button("Show less", key="btn_bio_less", className=GRAVATAR_BLUE):
                mt.session_state["bio_expanded"] = False
                mt.rerun()
        else:
            mt.write(PROFILE["bio"][:120] + "…")
            if mt.button("Show more", key="btn_bio_more", className=GRAVATAR_BLUE):
                mt.session_state["bio_expanded"] = True
                mt.rerun()

        mt.space(0.5)
        with mt.grid():
            with mt.row():
                with mt.col(6):
                    mt.button("Share", key="btn_share", className=f"w-full {GRAVATAR_BLUE}")
                with mt.col(6):
                    mt.button("Contact", key="btn_contact", className=f"w-full {GRAVATAR_BLUE}")

# ── verified accounts card ──────────────────────────────────────────────────
with mt.card("Verified Accounts"):
    for acct in ACCOUNTS:
        with mt.grid():
            with mt.row(className="items-center"):
                with mt.col(8):
                    mt.markdown(f"{acct['icon']}  **{acct['label']}**  ✓")
                    mt.write(acct["url"].removeprefix("https://"), className="text-sm opacity-70")
                with mt.col(4):
                    mt.link_button("Visit", url=acct["url"], new_tab=True, className=f"w-full {GRAVATAR_BLUE}")
        mt.markdown("---")

mt.markdown(
    "Built with **mxlit** — layout modeled after a Gravatar profile page. "
    "All names, roles, and links above are placeholder sample data."
)
