"""live_feed_demo.py — demonstrates mt.setInterval / mt.setTimeout.

Run with:
    mxlit run samples/live_feed_demo.py
"""
import math
import random
import time

import mxlit as mt

# ── Page setup ────────────────────────────────────────────────────────────────

mt.page_config(main_class="p-6 max-w-5xl mx-auto")
mt.title("Live Feed Demo")
mt.write(
    "Components inside `with mt.setInterval(sync_time=N)` blocks are refreshed "
    "automatically every **N seconds** via HTMX polling — no WebSockets needed."
)

# ── Sidebar: controls ─────────────────────────────────────────────────────────

with mt.sidebar():
    mt.header("Controls")
    interval = mt.slider("Refresh interval (s)", min_value=1, max_value=30, value=5,
                          key="lf_interval")
    history_len = mt.slider("History window", min_value=10, max_value=200, value=60,
                             key="lf_history_len")
    mt.write("---")
    if mt.button("Reset history", key="lf_reset"):
        mt.session_state["lf_points"] = []
        mt.session_state["lf_sine_points"] = []

# ── Data accumulation (runs on every /refresh POST) ───────────────────────────

now_ts = time.time()

# Scatter: random walk
points: list = mt.session_state.get("lf_points", [])
last_y = points[-1]["y"] if points else 0.0
new_y  = last_y + random.uniform(-2.0, 2.0)
points.append({"x": round(now_ts, 1), "y": round(new_y, 3)})
points = points[-history_len:]
mt.session_state["lf_points"] = points

# Line: sine wave sampled at current time
sine_points: list = mt.session_state.get("lf_sine_points", [])
sine_points.append({"x": round(now_ts, 1), "y": round(math.sin(now_ts * 0.5) * 10, 3)})
sine_points = sine_points[-history_len:]
mt.session_state["lf_sine_points"] = sine_points

# ── Layout: two-column chart area ─────────────────────────────────────────────

col_scatter, col_line = mt.columns(2)

with col_scatter:
    mt.subheader("Random Walk (Scatter)")
    with mt.setInterval(sync_time=interval):
        mt.scatter_chart(
            {"x": [p["x"] for p in points], "y": [p["y"] for p in points]},
            id="lf_scatter",
            class_="h-48",
        )
    mt.write(f"Points buffered: **{len(points)}** / {history_len}")

with col_line:
    mt.subheader("Sine Wave (Line)")
    with mt.setInterval(sync_time=interval):
        mt.line_chart(
            [p["y"] for p in sine_points],
            id="lf_sine",
            class_="h-48",
        )
    mt.write(f"Points buffered: **{len(sine_points)}** / {history_len}")

# ── Metrics row ───────────────────────────────────────────────────────────────

mt.header("Live Metrics")

m1, m2, m3, m4 = mt.columns(4)

with m1:
    with mt.setInterval(sync_time=interval):
        mt.metric("Latest Y", f"{new_y:+.2f}", delta=f"{new_y - last_y:+.2f}",
                  id="lf_metric_y")

with m2:
    with mt.setInterval(sync_time=interval):
        mt.metric("Min Y", f"{min(p['y'] for p in points):.2f}" if points else "—",
                  id="lf_metric_min")

with m3:
    with mt.setInterval(sync_time=interval):
        mt.metric("Max Y", f"{max(p['y'] for p in points):.2f}" if points else "—",
                  id="lf_metric_max")

with m4:
    with mt.setInterval(sync_time=interval):
        mt.metric("Refresh every", f"{interval}s", id="lf_metric_interval")

# ── One-shot delayed status (setTimeout) ──────────────────────────────────────

mt.header("setTimeout Demo")
mt.write(
    "The status banner below fetches once, **5 seconds after the page loads**, "
    "then stops — simulating a one-shot readiness check."
)

with mt.setTimeout(delay=5):
    mt.success(
        f"Data pipeline ready — {len(points)} points loaded as of "
        f"{time.strftime('%H:%M:%S', time.localtime(now_ts))}",
        id="lf_pipeline_status",
    )
