import streamlit as st
import pandas as pd
from datetime import datetime

# 🧠 Simulated cultural event-driven demand insights
CULTURAL_EVENTS = [
    {
        "event": "Diwali",
        "date": "2025-10-20",
        "region": "North India",
        "high_demand_skus": ["SKU012 - Sweets Box", "SKU019 - Diyas Pack", "SKU027 - Dry Fruits"],
        "confidence": "High"
    },
    {
        "event": "Pongal",
        "date": "2026-01-15",
        "region": "Tamil Nadu",
        "high_demand_skus": ["SKU033 - Jaggery", "SKU034 - Raw Rice", "SKU036 - Sugarcane Bundle"],
        "confidence": "Medium"
    },
    {
        "event": "Christmas",
        "date": "2025-12-25",
        "region": "Pan India",
        "high_demand_skus": ["SKU045 - Plum Cake", "SKU046 - Gifting Hamper", "SKU048 - Wine Bottle"],
        "confidence": "High"
    },
    {
        "event": "Ganesh Chaturthi",
        "date": "2025-09-06",
        "region": "Maharashtra",
        "high_demand_skus": ["SKU065 - Modak Mix", "SKU066 - Banana Leaf Pack", "SKU069 - Coconut"],
        "confidence": "Medium"
    },
]

# 📊 Demand Forecast Table
def create_forecast_df(events):
    data = []
    for e in events:
        for sku in e["high_demand_skus"]:
            data.append({
                "Event": e["event"],
                "Date": e["date"],
                "Region": e["region"],
                "SKU": sku,
                "Confidence": e["confidence"]
            })
    return pd.DataFrame(data)

# 🌐 Main Forecasting Tab
def show_forecasting_tab():
    st.header("📈 Culturally-Aware Demand Forecasting")
    st.markdown("""
    This module simulates how our AI anticipates SKU demand based on upcoming festivals, local events, and regional patterns. It empowers warehouses to stock proactively and avoid shortages.
    """)

    st.markdown("### 📅 Upcoming Events & Predicted Demand")
    df = create_forecast_df(CULTURAL_EVENTS)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Forecast Engine Insights")

    if st.button("🧠 Run Forecasting Engine"):
        st.success("✅ Forecasts updated successfully based on cultural and seasonal trends.")
        st.markdown("- Diwali sweets stock flagged as **URGENT** for North India.")
        st.markdown("- Christmas gifting inventory marked **under review** for Pan India.")
        st.markdown("- Pongal staples flagged for **early restocking** in Tamil Nadu.")
        st.markdown("- Modak Mix & coconuts for Ganesh Chaturthi demand rising.")
    else:
        st.info("Click the button to simulate trend-based demand forecasting.")

    st.markdown("---")
    st.markdown("### 🧾 Recommendations Summary")
    st.markdown("""
    - 🟢 **Flag critical SKUs** in high-demand zones 2–4 weeks ahead of events.
    - 🛒 **Trigger supplier restock alerts** for trending products.
    - 📦 **Coordinate with redistribution engine** to shift surplus inventory across regions.
    - 🔄 **Refresh forecasts weekly** using Google Trends + social media signals.
    """)
