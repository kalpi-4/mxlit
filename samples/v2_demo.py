"""
Demo script for Mxlit V2 reactive architecture.
Shows the new callback-based reactive system.
"""

import mxlit as mt

# UI Definition (runs once during init)
mt.title("Mxlit V2 Reactive Demo")

with mt.sidebar:
    region_filter = mt.selectbox("Select Region", ["North", "South", "East", "West"], key="region")

col1, col2 = mt.columns(2)
with col1:
    revenue_metric = mt.metric("Total Revenue", 0, id="revenue")
with col2:
    chart_placeholder = mt.write("Chart will appear here", id="chart")

# Reactive Data Callbacks (run on dependency changes)
@mt.callback(inputs=["region"], outputs=["revenue-value", "chart-content"])
def update_dashboard(region):
    # Simulate data processing
    revenue_data = {
        "North": 125000,
        "South": 98000,
        "East": 156000,
        "West": 87000
    }

    chart_data = f"Chart for {region}: Revenue = ${revenue_data.get(region, 0)}"

    return {
        "revenue-value": f"${revenue_data.get(region, 0):,}",
        "chart-content": chart_data
    }