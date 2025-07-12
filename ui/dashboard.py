import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_dashboard(inventory_path):
    st.header("📦 Warehouse Inventory Overview")

    df = pd.read_csv(inventory_path, parse_dates=['expiry_date'])

    st.dataframe(df, use_container_width=True)

    # ----------------------------------------
    # 📍 Expiry Timeline
    # ----------------------------------------
    st.markdown("#### 📍 Expiry Timeline")
    expiring_soon = df[df['expiry_date'] <= pd.to_datetime('today') + pd.Timedelta(days=2)]
    st.warning(f"{len(expiring_soon)} products expiring soon!", icon="⚠️")

    if not expiring_soon.empty:
        st.dataframe(expiring_soon[['sku_id', 'product_name', 'expiry_date', 'location']])

    # ----------------------------------------
    # 📊 Category-Wise Inventory Summary
    # ----------------------------------------
    st.subheader("📊 Category-Wise Inventory Summary")

    category_summary = df.groupby("category")["stock"].sum().sort_values(ascending=False)

    st.markdown("This chart shows total stock levels across each category. Useful for demand planning, restocking & redistribution focus.")

    fig, ax = plt.subplots(figsize=(7, 3))
    category_summary.plot(kind='bar', ax=ax, color="#36A2EB")
    ax.set_ylabel("Total Stock")
    ax.set_xlabel("Category")
    ax.set_title("Stock by Category")
    st.pyplot(fig)
