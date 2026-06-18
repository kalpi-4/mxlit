import mxlit as mt
import pandas as pd

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "save_success" not in mt.session_state:
    mt.session_state["save_success"] = False

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with mt.sidebar:
    mt.title("Oat Demo", className="text-lg font-bold")
    mt.markdown("---")

    mt.write("Navigation", className="text-xs font-semibold uppercase tracking-wide mb-2")
    mt.radio("", ["Dashboard", "Analytics", "Orders", "Settings"], key="nav_section")

    mt.markdown("---")

    mt.write("Theme", className="text-xs font-semibold uppercase tracking-wide mb-2")
    mt.selectbox("Color scheme", ["Default", "Slate", "Stone", "Rose", "Blue", "Green", "Orange"], key="theme_choice")

    auto_refresh = mt.toggle("Auto-refresh", value=False, key="auto_refresh")
    if auto_refresh:
        mt.info("Auto-refresh is on.")

    mt.markdown("---")
    mt.write("mxlit · FastAPI + HTMX", className="text-xs")

# ── PAGE TITLE ────────────────────────────────────────────────────────────────
mt.title("Dashboard", className="text-3xl font-bold")
mt.write(
    "This kitchensink dashboard shows various UI components and layouts built with **mxlit**.",
    className="mb-6",
)

# ── TOP METRICS ───────────────────────────────────────────────────────────────
with mt.card():
    with mt.grid():
        with mt.row():
            with mt.col(3): mt.metric("Revenue",      "$42,128", "+12.5% vs last month")
            with mt.col(3): mt.metric("Active Users", "2,847",   "-3.2% vs last month")
            with mt.col(3): mt.metric("Retention",    "3.24%",   "+0.8% vs last month")
            with mt.col(3): mt.metric("Uptime",       "99.99%",  "Healthy")

mt.markdown("---")

# ── TABS: OVERVIEW / PERFORMANCE / REPORTS ────────────────────────────────────
tab_overview, tab_performance, tab_reports = mt.tabs(["Overview", "Performance", "Reports"])

# ── Overview ──────────────────────────────────────────────────────────────────
with tab_overview:
    mt.subheader("Weekly Traffic")
    mt.write(
        "This dummy kitchensink dashboard page shows various UI components and "
        "layouts built with mxlit.",
        className="mb-3",
    )
    mt.line_chart(
        {"Mon": 420, "Tue": 380, "Wed": 510, "Thu": 460, "Fri": 590, "Sat": 340, "Sun": 280},
        className="rounded-lg border p-2",
    )

    mt.markdown("---")
    mt.subheader("Monthly Summary")
    mt.table(
        pd.DataFrame({
            "Metric":  ["Page Views", "Bounce Rate", "Avg Session Duration"],
            "Value":   ["128,450",    "42.3%",        "3m 24s"],
            "Change":  ["+8.2%",      "-1.4%",        "+0:18"],
        }),
        className="w-full",
    )

    mt.markdown("---")
    mt.subheader("Recent Activity")
    activities = [
        ("alice", "Submitted a new order #1042",   "2 min ago"),
        ("bob",   "Updated customer profile",       "15 min ago"),
        ("carol", "Generated monthly report",       "1 hr ago"),
        ("alice", "Resolved support ticket #88",    "3 hr ago"),
        ("bob",   "Deployed v2.4.1 to production",  "Yesterday"),
    ]
    for actor, desc, ts in activities:
        with mt.container(horizontal=True, className="items-center gap-3 py-2 border-b last:border-0"):
            mt.avatar(initials=actor[0].upper(), size="small")
            mt.write(f"**{actor}** — {desc}", className="flex-1 text-sm")
            mt.write(ts, className="text-xs shrink-0")

# ── Performance ───────────────────────────────────────────────────────────────
with tab_performance:
    mt.subheader("Performance Metrics")
    with mt.grid():
        with mt.row():
            with mt.col(4):
                mt.metric("Avg Response", "142 ms",    "p95: 380 ms",       className="w-full")
            with mt.col(4):
                mt.metric("Error Rate",   "0.03%",     "-0.01% this week",  className="w-full")
            with mt.col(4):
                mt.metric("Throughput",   "1,240 req/s", "+5% this week",   className="w-full")
    mt.spinner("small")

    mt.markdown("---")
    mt.subheader("Server Status")
    # Each stat rendered as label + meter (semantic colour cue) + detail line
    server_stats = [
        ("CPU Usage",   0.34, "8-core / 3.2 GHz"),
        ("Memory",      0.61, "9.8 GB / 16 GB"),
        ("Disk I/O",    0.12, "Read: 42 MB/s"),
        ("Network In",  0.08, "128 Mbps"),
        ("Network Out", 0.15, "240 Mbps"),
    ]
    _n = len(server_stats)
    _span = 12 // _n
    _last = 12 - _span * (_n - 1)
    with mt.grid():
        with mt.row():
            for _i, (label, val, detail) in enumerate(server_stats):
                with mt.col(_last if _i == _n - 1 else _span):
                    mt.write(label, className="text-xs font-semibold")
                    mt.meter(val, low=0.5, high=0.75, optimum=0.2)
                    mt.write(f"{int(val*100)}% — {detail}", className="text-xs")

    mt.markdown("---")
    mt.subheader("Response Time — last 7 days")
    mt.area_chart(
        {"Mon": 130, "Tue": 155, "Wed": 142, "Thu": 160, "Fri": 138, "Sat": 120, "Sun": 110},
        className="rounded-lg border p-2",
    )
    mt.subheader("Errors by Endpoint")
    mt.bar_chart(
        {"/api/orders": 12, "/api/users": 5, "/api/reports": 3, "/api/auth": 8, "/api/products": 1},
        className="rounded-lg border p-2",
    )

# ── Reports ───────────────────────────────────────────────────────────────────
with tab_reports:
    mt.breadcrumb([
        {"label": "Dashboard", "href": "#"},
        {"label": "Reports"},
    ])
    mt.subheader("Recent Orders")
    orders_df = pd.DataFrame({
        "Order ID":  ["#1042", "#1041", "#1040", "#1039", "#1038"],
        "Customer":  ["Alice Brown", "Bob Smith", "Carol Davis", "Dave Lee", "Eve Martin"],
        "Amount":    ["$320.00", "$89.50", "$1,200.00", "$45.00", "$670.00"],
        "Status":    ["Pending",  "Shipped", "Shipped",   "Pending", "Delivered"],
    })
    f_all, f_pending, f_shipped = mt.tabs(["All", "Pending", "Shipped"])
    with f_all:
        mt.dataframe(orders_df, className="w-full")
    with f_pending:
        mt.dataframe(
            orders_df[orders_df["Status"] == "Pending"].reset_index(drop=True),
            className="w-full",
        )
    with f_shipped:
        mt.dataframe(
            orders_df[orders_df["Status"].isin(["Shipped", "Delivered"])].reset_index(drop=True),
            className="w-full",
        )

    _order_page = mt.pagination(total_pages=5, current_page=1, key="orders_page")
    mt.write(f"Page **{_order_page}** of 5", className="text-xs")

    mt.markdown("---")
    mt.subheader("Notifications")
    with mt.grid():
        with mt.row():
            with mt.col(3): mt.info("System update available.")
            with mt.col(3): mt.success("Report generated.")
            with mt.col(3): mt.warning("Disk usage high.")
            with mt.col(3): mt.error("Payment failed.")

mt.markdown("---")

# ── FAQ ───────────────────────────────────────────────────────────────────────
mt.header("FAQ", className="font-bold border-b pb-1")

with mt.expander("How do I reset my password?", className="border rounded-lg mb-2"):
    mt.write(
        "Go to **Settings → Security** and click *Reset Password*. "
        "A reset link will be sent to your registered email address."
    )

with mt.expander("What export formats are supported?", className="border rounded-lg mb-2"):
    mt.write("Reports can be exported as **CSV**, **Excel (.xlsx)**, **JSON**, and **PDF**.")

with mt.expander("How is billing calculated?", className="border rounded-lg mb-2"):
    mt.write(
        "Billing is calculated monthly based on the number of active seats and API calls "
        "made during the billing cycle. Overages are billed at the standard rate shown on "
        "your plan page."
    )

with mt.expander("Can I connect third-party integrations?", className="border rounded-lg mb-2"):
    mt.write("Yes — integrations are available via the REST API. Example:")
    mt.code(
        'curl -X POST https://api.example.com/hooks \\\n'
        '  -H "Authorization: Bearer <TOKEN>" \\\n'
        '  -d \'{"event": "order.created", "url": "https://your-site.com/webhook"}\'',
        className="text-xs",
    )

mt.markdown("---")

# ── ACCOUNT SETTINGS ─────────────────────────────────────────────────────────
mt.header("Account Settings", className="font-bold border-b pb-1")

with mt.grid():
    with mt.row():
        with mt.col(6):
            mt.subheader("Profile", className="font-semibold mb-2")
            name  = mt.text_input("Full Name",   value="Alice Brown",            key="acc_name")
            email = mt.email_input("Email",      value="alice@example.com",      key="acc_email")
            role  = mt.selectbox("Role", ["Admin", "Editor", "Viewer"],           key="acc_role")
            start = mt.date_input("Start Date",  value="2024-01-15",              key="acc_start")
            bio   = mt.text_area("Bio",          value="Product designer at Oat.", key="acc_bio")
            brand = mt.color_picker("Brand Color", value="#415F91",               key="acc_brand")
        with mt.col(6):
            mt.subheader("Preferences", className="font-semibold mb-2")
            mt.slider("Notification Volume", 0, 100, 60, key="acc_volume")

            mt.write("Email preferences", className="text-sm font-medium mt-3 mb-1")
            mt.checkbox("Product updates",  value=True,  key="acc_email_product")
            mt.checkbox("Marketing emails", value=False, key="acc_email_mkt")
            mt.checkbox("Security alerts",  value=True,  key="acc_email_security")

            mt.write("Theme", className="text-sm font-medium mt-3 mb-1")
            mt.radio("", ["Light", "Dark", "System"], key="acc_theme_pref")

            mt.write("Security", className="text-sm font-medium mt-3 mb-1")
            mt.toggle("Two-factor authentication", value=True,  key="acc_2fa")
            mt.toggle("API access",                value=False, key="acc_api")

mt.markdown("---")

# Action buttons — Save / Cancel / Delete (delete uses mt.dialog for confirmation)
with mt.grid():
    with mt.row():
        with mt.col(6):
            if mt.button("Save Changes", className="w-full"):
                mt.session_state["save_success"] = True
        with mt.col(3):
            mt.button("Cancel", key="btn_cancel", className="w-full")
        with mt.col(3):
            with mt.dialog("Delete Account", trigger_label="Delete Account"):
                mt.warning("Are you sure? All data will be permanently removed.")
                if mt.button("Yes, delete my account", key="confirm_delete"):
                    mt.error("Account deletion is disabled in this demo.")

# Toast replaces the inline success banner
if mt.session_state.get("save_success"):
    mt.toast(f"Changes saved for {name}.", title="Saved", variant="success")
    mt.session_state["save_success"] = False
