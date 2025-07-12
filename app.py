import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# Module imports
from ui.dashboard import show_dashboard
from ui.redistribution import show_redistribution_tab, show_agent_summary
from ui.forecasting import show_forecasting_tab  # ✅ Updated import to correct function
from agents.expiry_agent import run_redistribution  # Agent simulation logic

INVENTORY_PATH = "data/inventory.csv"

# ------------------------------
# Page Setup
# ------------------------------
st.set_page_config(page_title="EcoTwin Microhub", layout="wide")

# ------------------------------
# Sidebar Navigation
# ------------------------------
st.sidebar.title("🔧 EcoTwin Navigation")
page = st.sidebar.radio("Go to", [
    "🏠 Dashboard",
    "🔄 Redistribution",
    "📈 Culturally-Aware Forecasting",
    "📊 Agent Summary"
])

# ------------------------------
# Helper: Load inventory
# ------------------------------
@st.cache_data
def load_inventory(path):
    return pd.read_csv(path)

# ------------------------------
# Helper: Get upcoming expiry data (next 3–5 days)
# ------------------------------
def get_next_expiring_items(df):
    expiry_col = "expiry_date"
    df[expiry_col] = pd.to_datetime(df[expiry_col])
    today = pd.to_datetime(datetime.now().date())

    start_date = today + timedelta(days=3)
    end_date = today + timedelta(days=5)

    st.caption(f"📅 Showing SKUs expiring between **{start_date.date()}** and **{end_date.date()}**")

    filtered = df[
        (df[expiry_col] >= start_date) &
        (df[expiry_col] <= end_date)
    ]

    return filtered[["sku_id", "product_name", expiry_col, "stock", "location"]].rename(
        columns={
            expiry_col: "expiry",
            "product_name": "product",
            "location": "zone"
        }
    ).sort_values("expiry")

# ------------------------------
# Page Routing
# ------------------------------
if page == "🏠 Dashboard":
    show_dashboard(INVENTORY_PATH)

elif page == "🔄 Redistribution":
    show_redistribution_tab(INVENTORY_PATH)

elif page == "📈 Culturally-Aware Forecasting":
    show_forecasting_tab()  # ✅ FIXED: now calling the correct function

elif page == "📊 Agent Summary":
    st.title("📊 Agent Summary")

    inventory_df = load_inventory(INVENTORY_PATH)
    redis_df, stock_saved = run_redistribution(INVENTORY_PATH)
    next_expiring = get_next_expiring_items(inventory_df)

    buyer_stats = {
        "matched": len(redis_df) * 3,
        "accepted": sum(random.random() < 0.3 for _ in range(len(redis_df) * 3)),
        "unsold": len(redis_df) - int(len(redis_df) * 0.3),
        "stock_saved": stock_saved
    }

    show_agent_summary(redis_df, buyer_stats, next_expiring)
