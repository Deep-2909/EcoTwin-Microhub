import streamlit as st
import pandas as pd
import csv
from datetime import date, datetime, timedelta
import hashlib

# ----------------------------
# Load Events from CSV
# ----------------------------
@st.cache_data
def load_cultural_events(path="data/cultural_events.csv"):
    events = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append({
                "event": row["event"],
                "date": row["date"],
                "region": row["region"],
                "high_demand_skus": [sku.strip() for sku in row["high_demand_skus"].split(";")],
                "confidence": row["confidence"]
            })
    return events


# ----------------------------
# Deterministic SKU-based Stock Generation
# ----------------------------
def deterministic_hash(sku_name):
    return int(hashlib.md5(sku_name.encode()).hexdigest(), 16)

def generate_stock_and_demand(sku_name):
    hash_val = deterministic_hash(sku_name)
    current_stock = 80 + (hash_val % 71)  # Range: 80–150
    expected_demand = 120 + (hash_val % 101)  # Range: 120–220
    return current_stock, expected_demand


# ----------------------------
# Main Forecasting Tab
# ----------------------------
def show_forecasting_tab():
    st.title("🧠 Culturally-Aware Demand Forecasting")
    st.markdown("This module simulates how our AI anticipates SKU demand based on upcoming festivals, local events, and regional patterns. It empowers warehouses to stock proactively and avoid shortages.")

    scraped_events = load_cultural_events()

    today = datetime.today().date()
    detection_window_days = 45
    window_end = today + timedelta(days=detection_window_days)

    # Only show events within 45-day window
    visible_events = [
        e for e in scraped_events
        if today <= datetime.strptime(e["date"], "%Y-%m-%d").date() <= window_end
    ]

    # 📅 Calendar Explorer
    st.subheader("📅 Calendar Explorer")
    selected_date = st.date_input("Open calendar to explore dates:", date.today())
    matched_events = [
        e for e in scraped_events
        if e["date"] == selected_date.strftime("%Y-%m-%d")
    ]

    # If user selects a valid cultural event manually, add it
    if matched_events:
        for event in matched_events:
            if event not in visible_events:
                visible_events.append(event)

    # 🔍 Show Detected Events
    st.subheader("🔍 Upcoming Events Detected by Scraper")
    if visible_events:
        for e in sorted(visible_events, key=lambda x: x["date"]):
            badge = "🟢" if e["confidence"] == "High" else "🟡"
            st.markdown(f"- {badge} **{e['event']}** — `{e['date']}` in *{e['region']}* ({e['confidence']})")
    else:
        st.info("🤖 No cultural events detected in the upcoming days.")

    # 📦 SKU Recommendations
    sku_recommendations = []
    for idx, e in enumerate(visible_events):
        for sku in e["high_demand_skus"]:
            current_stock, expected_demand = generate_stock_and_demand(sku)
            sku_recommendations.append({
                "sku_id": f"SKU{900 + idx}{e['high_demand_skus'].index(sku)}",
                "product_name": sku,
                "event": e["event"],
                "region": e["region"],
                "confidence": e["confidence"],
                "current_stock": current_stock,
                "expected_demand": expected_demand,
            })

    simulate_trend_spike = st.toggle("📈 Simulate Trend Spike (30% Increase in Demand)")

    for rec in sku_recommendations:
        base_demand = rec["expected_demand"]
        if simulate_trend_spike:
            rec["expected_demand"] = int(base_demand * 1.3)

        rec["stock_gap"] = rec["expected_demand"] - rec["current_stock"]
        rec["action"] = (
            "⚠️ Restock Needed" if rec["stock_gap"] > 0 else
            "✅ Overstocked" if rec["stock_gap"] < 0 else
            "✔️ Just In Time"
        )

    df_recommend = pd.DataFrame(sku_recommendations)

    # 🎯 Filters
    st.subheader("💕 Filter Recommendations")
    col1, col2 = st.columns(2)
    with col1:
        event_filter = st.selectbox("Filter by Event", ["All"] + sorted(df_recommend["event"].unique()))
    with col2:
        region_filter = st.selectbox("Filter by Region", ["All"] + sorted(df_recommend["region"].unique()))

    filtered_df = df_recommend.copy()
    if event_filter != "All":
        filtered_df = filtered_df[filtered_df["event"] == event_filter]
    if region_filter != "All":
        filtered_df = filtered_df[filtered_df["region"] == region_filter]

    # 🎯 Selected Date Feedback
    if matched_events:
        st.success(f"🎯 Cultural Event(s) on {selected_date}:")
        for e in matched_events:
            st.markdown(f"- **{e['event']}** in *{e['region']}* → SKUs: {', '.join(e['high_demand_skus'])}")
    else:
        st.info("No major cultural event on this selected date.")

    # 📦 Final Table
    st.subheader("📦 SKU Stocking Recommendations")
    st.dataframe(filtered_df, use_container_width=True)

    # 📊 Insights
    st.subheader("📊 Forecast Engine Insights")
    st.success("✅ Forecasts updated based on scraper-detected events.")
    st.markdown("- Upcoming festival SKUs flagged based on expected demand & regional trends.")
    if simulate_trend_spike:
        st.markdown("- 📈 Simulated trend surge applied (30% demand spike).")

    # 📥 Summary
    st.markdown("---")
    st.markdown("### 🧾 Recommendations Summary")
    st.markdown("""
    - 🟢 **Flag critical SKUs** in high-demand zones 2–4 weeks ahead of events.  
    - 🛒 **Trigger supplier restock alerts** for trending products.  
    - 📦 **Coordinate with redistribution engine** to shift surplus inventory across regions.  
    - 🔄 **Refresh forecasts weekly** using Google Trends + social media signals.  
    """)

    with st.expander("📥 Download Filtered Recommendations"):
        st.download_button(
            label="Download as CSV",
            data=filtered_df.to_csv(index=False),
            file_name="stocking_recommendations.csv",
            mime="text/csv"
        )
