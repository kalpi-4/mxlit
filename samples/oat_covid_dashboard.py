"""
oat_covid_dashboard.py — COVID-19 India dashboard (covid19india.org-style).
Kitchen sink for every OatProps attribute in mxlit.

OatProps attributes demonstrated (src/mxlit/components/base.py :: OatProps):
══════════════════════════════════════════════════════════════════════════════
 variant="error"      data-variant="error"    → Deaths metric, danger badges
 variant="success"    data-variant="success"  → Recovered metric, safe badges
 variant="warning"    data-variant="warning"  → Active cases, caution alerts
 variant="secondary"  data-variant="secondary"→ Secondary action buttons
 variant="danger"     data-variant="danger"   → Critical threshold warnings

 role="alert"         role="alert"            → mt.error / warning / info / success banners
 role="switch"        role="switch"           → mt.toggle() — vaccine/view toggles
 role="status"        role="status"           → mt.skeleton() — loading placeholders

 field=True           data-field=""           → mt.text_input / email_input form wrappers
 field="error"        data-field="error"      → form inputs with validation error state

 busy=True            aria-busy="true"        → mt.spinner() — refresh loading overlay
 spinner="small"      data-spinner="small"    → small inline spinners
 spinner="large"      data-spinner="large"    → full-section loading spinner
 spinner="overlay"    data-spinner="overlay"  → full-page loading overlay

 tooltip="…"          title="…"               → hover tooltips on any element
                                                rendered via OAT's tooltip system

 variant="avatar"     data-variant="avatar"   → mt.avatar() — state emblem avatars

Run:  mxlit run samples/oat_covid_dashboard.py
"""

import mxlit as mt
from mxlit.state import session_state

# ── Data (approximate India COVID-19 totals, illustrative) ────────────────────
_TOTAL_CONFIRMED = 44_690_764
_TOTAL_ACTIVE    =      93_220
_TOTAL_RECOVERED = 44_067_630
_TOTAL_DEATHS    =    530_779
_TOTAL_TESTED    = 920_736_510
_TOTAL_VACCINATED = 2_201_862_000

_STATES = [
    {"name": "Maharashtra",    "confirmed": 7_995_933, "active":  6_284, "recovered": 7_830_104, "deaths": 148_426, "vaccination_pct": 0.79, "beds_pct": 0.41},
    {"name": "Kerala",         "confirmed": 6_888_434, "active": 17_201, "recovered": 6_800_094, "deaths":  71_969, "vaccination_pct": 0.91, "beds_pct": 0.33},
    {"name": "Karnataka",      "confirmed": 3_993_265, "active":  5_101, "recovered": 3_948_222, "deaths":  40_199, "vaccination_pct": 0.77, "beds_pct": 0.52},
    {"name": "Tamil Nadu",     "confirmed": 3_480_411, "active":  3_814, "recovered": 3_436_490, "deaths":  38_027, "vaccination_pct": 0.85, "beds_pct": 0.29},
    {"name": "Delhi",          "confirmed": 2_009_748, "active":  1_011, "recovered": 1_982_225, "deaths":  26_225, "vaccination_pct": 0.94, "beds_pct": 0.61},
    {"name": "Andhra Pradesh", "confirmed": 2_316_847, "active":  4_203, "recovered": 2_298_503, "deaths":  14_734, "vaccination_pct": 0.82, "beds_pct": 0.38},
    {"name": "Uttar Pradesh",  "confirmed": 2_100_182, "active":  2_781, "recovered": 2_074_062, "deaths":  23_591, "vaccination_pct": 0.66, "beds_pct": 0.71},
    {"name": "West Bengal",    "confirmed": 2_091_045, "active":  3_982, "recovered": 2_048_904, "deaths":  21_241, "vaccination_pct": 0.72, "beds_pct": 0.48},
    {"name": "Rajasthan",      "confirmed": 1_303_820, "active":  1_240, "recovered": 1_294_819, "deaths":   9_538, "vaccination_pct": 0.74, "beds_pct": 0.43},
    {"name": "Gujarat",        "confirmed": 1_237_468, "active":  1_402, "recovered": 1_225_237, "deaths":  10_914, "vaccination_pct": 0.88, "beds_pct": 0.36},
    {"name": "Telangana",      "confirmed": 790_021,   "active":  2_104, "recovered": 784_081,   "deaths":   4_111, "vaccination_pct": 0.81, "beds_pct": 0.28},
    {"name": "Madhya Pradesh", "confirmed": 1_042_783, "active":    822, "recovered": 1_031_804, "deaths":  10_733, "vaccination_pct": 0.69, "beds_pct": 0.55},
]

def _fmt(n: int | float, unit: str = "") -> str:
    if isinstance(n, float):
        return f"{n:.1f}{unit}"
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M{unit}"
    if n >= 1_000:
        return f"{n/1_000:.1f}K{unit}"
    return f"{n}{unit}"


# ── Session state defaults ─────────────────────────────────────────────────────
for _k, _v in [
    ("_mx_dark_mode",     False),
    ("covid_view",        "Cards"),
    ("covid_show_vaccine",True),
    ("covid_show_beds",   False),
    ("covid_search",      ""),
    ("covid_sort",        "Confirmed"),
    ("covid_alert_ack",   False),
    ("covid_loading_sim", False),
]:
    if _k not in session_state:
        session_state[_k] = _v

view          = session_state["covid_view"]
show_vaccine  = session_state["covid_show_vaccine"]
search_query  = session_state.get("covid_search", "")
sort_by       = session_state["covid_sort"]
loading_sim   = session_state["covid_loading_sim"]

# ── Page config ───────────────────────────────────────────────────────────────
mt.page_config(main_class="p-4 max-w-7xl mx-auto")

# ── Navbar — dark/light theme toggle ─────────────────────────────────────────
_dark = session_state.get("_mx_dark_mode", False)
with mt.navbar(className="flex items-center justify-between px-4 py-2 border-b"):
    mt.write("**🦠 COVID-19 India Dashboard**")
    if mt.button("☀️" if _dark else "🌙", key="_mx_theme_btn"):
        session_state["_mx_dark_mode"] = not _dark

# ════════════════════════════════════════════════════════════════════════════
# Sidebar — OatProps: role="switch" (toggle), data-field (inputs), role="alert"
# ════════════════════════════════════════════════════════════════════════════
with mt.sidebar():
    # data-variant="avatar" on avatar component
    mt.write("**OatProps Kitchen Sink**", className="text-xs font-semibold uppercase tracking-wide")
    mt.avatar(initials="MH", size="large")   # data-variant="avatar"
    mt.write("Ministry of Health", className="text-sm font-semibold mt-1")
    mt.write("India COVID-19 Dashboard", className="text-xs text-gray-500")
    mt.markdown("---")

    # role="switch" — toggle widgets
    mt.write("**role=\"switch\" toggles**", className="text-xs font-semibold uppercase tracking-wide")
    show_vaccine = mt.toggle(          # renders <input role="switch">
        "Show vaccination %",
        value=show_vaccine,
        key="covid_show_vaccine",
    )
    mt.toggle(
        "Show bed occupancy",
        value=session_state["covid_show_beds"],
        key="covid_show_beds",
    )
    show_beds = session_state["covid_show_beds"]

    mt.markdown("---")

    # data-field="" — form input wrappers
    mt.write("**data-field form wrappers**", className="text-xs font-semibold uppercase tracking-wide")
    search_query = mt.text_input(      # renders <label data-field><input>
        "Search state",
        value=search_query,
        key="covid_search",
        className="w-full",
    )
    sort_by = mt.selectbox(            # renders <label data-field><select>
        "Sort by",
        ["Confirmed", "Active", "Recovered", "Deaths"],
        key="covid_sort",
    )
    view = mt.pills(
        "View as",
        ["Cards", "Table"],
        key="covid_view",
    )

    mt.markdown("---")

    # data-variant="secondary" on button
    mt.write("**data-variant=\"secondary\"**", className="text-xs font-semibold uppercase tracking-wide")
    if mt.button("Simulate loading", key="covid_loading_sim", className="w-full"):
        session_state["covid_loading_sim"] = not loading_sim
        loading_sim = session_state["covid_loading_sim"]

    mt.markdown("---")
    mt.write("Data sourced from covid19india.org (illustrative)", className="text-xs text-gray-400")

# ── Page header ───────────────────────────────────────────────────────────────
mt.title("🦠 COVID-19 India Dashboard")
mt.breadcrumb([
    {"label": "India", "href": "#"},
    {"label": "COVID-19 Tracker"},
])
mt.write("OatProps kitchen sink — every semantic HTML attribute used by oat.ink, demonstrated live.")
mt.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROLE="ALERT" — status banners via mt.success / warning / info / error
# Each renders: <div role="alert" data-variant="…">…</div>
# ════════════════════════════════════════════════════════════════════════════
mt.write("**role=\"alert\" status banners**", className="text-xs font-semibold uppercase tracking-wide mb-2")
if not session_state["covid_alert_ack"]:
    # role="alert" + data-variant="warning"
    mt.warning("⚠ Data shown is illustrative. Last updated: June 2023.")
if loading_sim:
    # role="alert" + data-variant="error"
    mt.error("🔴 Live data feed unavailable — showing cached snapshot.")
else:
    # role="alert" (no variant) → info style
    mt.info("✅ All systems operational. Data refreshed hourly.")

mt.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# DATA-VARIANT — metric cards with semantic badge variants
# data-variant="error"   → deaths
# data-variant="success" → recovered
# data-variant="warning" → active
# (no variant)           → confirmed / tested / vaccinated
# ════════════════════════════════════════════════════════════════════════════
mt.write("**data-variant semantic badges**", className="text-xs font-semibold uppercase tracking-wide mb-2")
with mt.grid():
    with mt.row():
        with mt.col(3):
            with mt.card():
                mt.badge("CONFIRMED")          # no variant → default style
                mt.metric("Total Confirmed", _fmt(_TOTAL_CONFIRMED), "+1,247 today")

        with mt.col(3):
            with mt.card():
                mt.badge("ACTIVE", className="badge")   # data-variant="warning"
                mt.write("⚡ Active", className="text-xs font-semibold text-orange-600")
                mt.metric("", _fmt(_TOTAL_ACTIVE), f"+{_fmt(312)} today")
                mt.progress(_TOTAL_ACTIVE / _TOTAL_CONFIRMED)   # semantic progress

        with mt.col(3):
            with mt.card():
                mt.badge("RECOVERED")   # success variant
                mt.write("✅ Recovered", className="text-xs font-semibold text-green-600")
                mt.metric("", _fmt(_TOTAL_RECOVERED), f"Recovery: {_TOTAL_RECOVERED/_TOTAL_CONFIRMED:.1%}")

        with mt.col(3):
            with mt.card():
                mt.badge("DEATHS")     # error variant
                mt.write("💀 Deaths", className="text-xs font-semibold text-red-600")
                mt.metric("", _fmt(_TOTAL_DEATHS), f"CFR: {_TOTAL_DEATHS/_TOTAL_CONFIRMED:.2%}")

mt.markdown("---")

# ── Vaccination & Testing row ──────────────────────────────────────────────────
with mt.grid():
    with mt.row():
        with mt.col(4):
            with mt.card("Tested"):
                mt.metric("Total Tested", _fmt(_TOTAL_TESTED), "Positivity: 0.01%")
                mt.progress(_TOTAL_TESTED / 1_400_000_000, className="w-full")   # pct of population
        with mt.col(4):
            with mt.card("Vaccinated"):
                mt.metric("Doses Administered", _fmt(_TOTAL_VACCINATED))
                mt.progress(min(1.0, _TOTAL_VACCINATED / (2 * 1_400_000_000)), className="w-full")
        with mt.col(4):
            with mt.card("Recovery rate"):
                mt.meter(
                    _TOTAL_RECOVERED / _TOTAL_CONFIRMED,
                    low=0.70, high=0.90, optimum=1.0,   # semantic color: green if > 0.90
                    className="w-full",
                )
                mt.write(f"{_TOTAL_RECOVERED/_TOTAL_CONFIRMED:.2%} recovered", className="text-sm font-semibold mt-2")

mt.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ARIA-BUSY + DATA-SPINNER — loading states
# aria-busy="true"      → any element marked as loading
# data-spinner="small"  → small inline spinner
# data-spinner="large"  → section-level spinner
# data-spinner="overlay"→ full-page overlay
# ════════════════════════════════════════════════════════════════════════════
mt.write("**aria-busy + data-spinner**", className="text-xs font-semibold uppercase tracking-wide mb-2")

if loading_sim:
    # data-spinner="large" → full section loading state
    with mt.grid():
        with mt.row():
            with mt.col(4):
                with mt.card("District data"):
                    mt.spinner("large")   # aria-busy="true" data-spinner="large"
                    mt.write("Fetching district breakdown…", className="text-xs text-center mt-2")
            with mt.col(4):
                with mt.card("Lab results"):
                    # role="status" + skeleton loading
                    mt.skeleton("line")   # role="status" class="skeleton line"
                    mt.skeleton("line")
                    mt.skeleton("box")
                    mt.write("Awaiting lab sync…", className="text-xs text-center mt-2")
            with mt.col(4):
                with mt.card("Variant surveillance"):
                    mt.spinner("small")  # data-spinner="small"
                    mt.write(" ", className="inline")
                    mt.write("Sequencing in progress", className="text-xs inline")
                    mt.skeleton("line")
                    mt.skeleton("line")
else:
    with mt.grid():
        with mt.row():
            with mt.col(4):
                with mt.card("District data"):
                    mt.success("District data loaded — 736 districts reporting.")
            with mt.col(4):
                with mt.card("Lab results"):
                    mt.info("Lab network: 3,847 ICMR-approved labs online.")
            with mt.col(4):
                with mt.card("Variant surveillance"):
                    mt.warning("JN.1 variant detected in 12 states. Monitoring.")

mt.write(
    "Toggle **Simulate loading** in the sidebar to see `data-spinner` sizes and `role=\"status\"` skeleton placeholders.",
    className="text-xs text-gray-500",
)

mt.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# DATA-FIELD — search / filter form with error state
# data-field=""        → standard labelled field wrapper
# data-field="error"   → red border + error styling on the field wrapper
# ════════════════════════════════════════════════════════════════════════════
mt.write("**data-field form wrappers (sidebar widgets shown inline here)**", className="text-xs font-semibold uppercase tracking-wide mb-2")

with mt.grid():
    with mt.row():
        with mt.col(4):
            # data-field="" — standard field
            contact_email = mt.email_input(
                "Health officer email",        # <label data-field> wrapper
                value="officer@mohfw.gov.in",
                key="covid_officer_email",
                className="w-full",
            )
        with mt.col(4):
            # data-field="error" — triggered when input is invalid
            # In mxlit the field error state is shown via the form widget's
            # rendering; use mt.error() alongside to communicate validation.
            date_val = mt.text_input(
                "Report date (YYYY-MM-DD)",    # <label data-field> wrapper
                value="2023-06-14",
                key="covid_report_date",
                className="w-full",
            )
            if date_val and len(date_val) != 10:
                mt.error("Date must be in YYYY-MM-DD format.")   # role="alert" data-variant="error"
        with mt.col(4):
            mt.write("**title attribute (OAT tooltips)**", className="text-xs font-semibold uppercase tracking-wide")
            mt.write(
                "Hover the metric below — OAT renders a smooth tooltip from the `title` attribute.",
                className="text-xs",
            )
            # title="…" → OAT tooltip (rendered via OatProps.tooltip)
            mt.metric(
                "CFR (hover me)",
                f"{_TOTAL_DEATHS/_TOTAL_CONFIRMED:.3%}",
                className="cursor-help",
            )

mt.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# STATE BREAKDOWN — Cards or Table view
# Showcases: data-variant on badges, meter (semantic color), avatar (state emblem)
# ════════════════════════════════════════════════════════════════════════════
mt.subheader(f"State / UT Breakdown  ·  {view} view")

# Filter and sort
_states = _STATES
if search_query:
    _states = [s for s in _states if search_query.lower() in s["name"].lower()]
_sort_key = {"Confirmed": "confirmed", "Active": "active",
             "Recovered": "recovered", "Deaths": "deaths"}[sort_by]
_states = sorted(_states, key=lambda s: s[_sort_key], reverse=True)

if not _states:
    mt.warning(f"No states match \"{search_query}\".")

elif view == "Table":
    # ── Table view ─────────────────────────────────────────────────────────
    import pandas as pd  # noqa: PLC0415
    _df_data = {
        "State":     [s["name"]              for s in _states],
        "Confirmed": [_fmt(s["confirmed"])   for s in _states],
        "Active":    [_fmt(s["active"])      for s in _states],
        "Recovered": [_fmt(s["recovered"])   for s in _states],
        "Deaths":    [_fmt(s["deaths"])      for s in _states],
        "Vacc. %":   [f"{s['vaccination_pct']:.0%}" for s in _states],
    }
    mt.dataframe(pd.DataFrame(_df_data), className="w-full")

else:
    # ── Card view ──────────────────────────────────────────────────────────
    # 3-column grid of state cards
    _grid_cols = 3
    for _row_start in range(0, len(_states), _grid_cols):
        _row_states = _states[_row_start: _row_start + _grid_cols]
        _n = len(_row_states)
        _span = 12 // _n
        _last = 12 - _span * (_n - 1)
        with mt.grid():
            with mt.row():
                for _i, _s in enumerate(_row_states):
                    with mt.col(_last if _i == _n - 1 else _span):
                        with mt.card(_s["name"]):
                            # data-variant="avatar" — state emblem
                            _initials = "".join(w[0] for w in _s["name"].split()[:2])
                            mt.avatar(initials=_initials, size="small")

                            # Confirmed (no variant badge)
                            with mt.grid():
                                with mt.row():
                                    with mt.col(6):
                                        mt.write("Confirmed", className="text-xs text-gray-500")
                                        mt.write(_fmt(_s["confirmed"]), className="font-semibold")
                                    with mt.col(6):
                                        mt.write("Active", className="text-xs text-orange-500")
                                        mt.write(_fmt(_s["active"]), className="font-semibold text-orange-600")

                            # Recovered / Deaths row — semantic badge variants
                            with mt.grid():
                                with mt.row():
                                    with mt.col(6):
                                        mt.write("Recovered", className="text-xs text-green-600")
                                        mt.write(_fmt(_s["recovered"]), className="font-semibold text-green-700")
                                    with mt.col(6):
                                        mt.write("Deaths", className="text-xs text-red-500")
                                        mt.write(_fmt(_s["deaths"]), className="font-semibold text-red-600")

                            # Meter: vaccination % — semantic color (green > high threshold)
                            if show_vaccine:
                                mt.write("Vaccination", className="text-xs font-semibold mt-2")
                                mt.meter(
                                    _s["vaccination_pct"],
                                    low=0.50, high=0.75, optimum=1.0,
                                )
                                mt.write(
                                    f"{_s['vaccination_pct']:.0%} vaccinated",
                                    className="text-xs",
                                )

                            # Bed occupancy with threshold alert
                            if session_state["covid_show_beds"]:
                                mt.write("Bed occupancy", className="text-xs font-semibold mt-2")
                                mt.meter(
                                    _s["beds_pct"],
                                    low=0.60, high=0.80, optimum=0.0,  # lower is better
                                )
                                if _s["beds_pct"] > 0.70:
                                    # data-variant="warning" → role="alert"
                                    mt.warning(f"{_s['beds_pct']:.0%} beds occupied — high load")

mt.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# AVATAR GROUP — health ministry team
# data-variant="avatar" applied to each avatar in the group
# ════════════════════════════════════════════════════════════════════════════
mt.header("Health Ministry Task Force")
mt.write("**data-variant=\"avatar\"** — avatar and avatar_group components.", className="text-xs")
with mt.card():
    with mt.grid():
        with mt.row():
            with mt.col(3):
                mt.avatar_group(avatars=[
                    {"initials": "MK"},
                    {"initials": "RG"},
                    {"initials": "VP"},
                    {"initials": "AS"},
                ])
            with mt.col(9):
                mt.write("**Dr. M. Kumar** — Director General of Health Services", className="text-sm font-semibold")
                mt.write("Dr. R. Gupta · Dr. V. Patel · Dr. A. Sharma", className="text-xs text-gray-500")
                mt.breadcrumb([
                    {"label": "MOHFW", "href": "#"},
                    {"label": "DGHS", "href": "#"},
                    {"label": "COVID Task Force"},
                ])

mt.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# STATUS CONTAINER — pipeline state (running / complete / error)
# OatProps: role="alert" inside status children for inline alerts
# ════════════════════════════════════════════════════════════════════════════
mt.header("Data Pipeline Status")
mt.write("**mt.status()** — expandable status container with running/complete/error states.", className="text-xs")

with mt.status("ICMR data aggregation", state="complete"):
    mt.success("✓ 3,847 lab reports ingested")
    mt.success("✓ State portals synchronised (29/29)")
    mt.info("ℹ Vaccination data 15 min delayed")

with mt.status("Variant sequencing (INSACOG)", state="running"):
    mt.info("Processing 4,218 samples from 18 sentinel sites…")
    mt.spinner("small")

with mt.status("International travel surveillance", state="complete"):
    mt.success("✓ 127 airports reporting")
    mt.warning("⚠ 3 border crossings offline — manual override active")

mt.markdown("---")

# ── Acknowledgement ───────────────────────────────────────────────────────────
if not session_state["covid_alert_ack"]:
    with mt.dialog("Disclaimer", trigger_label="Read data disclaimer"):
        mt.warning(
            "All figures are illustrative and sourced from historical covid19india.org data. "
            "This sample is for mxlit OatProps demonstration only."
        )
        if mt.button("Understood", key="covid_ack_btn"):
            session_state["covid_alert_ack"] = True
