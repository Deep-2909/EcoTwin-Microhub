import streamlit as st
import pandas as pd

def show_dashboard(inventory_path):
    st.header("📦 Warehouse Inventory Overview")

    df = pd.read_csv(inventory_path, parse_dates=['expiry_date'])

    st.dataframe(df, use_container_width=True)

    st.markdown("#### 📍 Expiry Timeline")
    expiring_soon = df[df['expiry_date'] <= pd.to_datetime('today') + pd.Timedelta(days=2)]
    st.warning(f"{len(expiring_soon)} products expiring soon!", icon="⚠️")

    if not expiring_soon.empty:
        st.dataframe(expiring_soon[['sku_id', 'product_name', 'expiry_date', 'location']])
