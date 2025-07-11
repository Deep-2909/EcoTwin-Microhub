import streamlit as st
import base64
import os
import time
import random
import pandas as pd
from agents.expiry_agent import run_redistribution, rank_buyers_for_sku

# 🔧 Convert image file to base64
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 📦 Notification channel → icon path
icon_map = {
    "WhatsApp": "assets/whatsapp.png",
    "Email": "assets/gmail.png",
    "Slack": "assets/slack.png",
    "SMS": "assets/sms.png"
}

# 🧠 Simulate buyer response with delay & probability
def simulate_buyer_response(buyer):
    delay = random.uniform(0.8, 1.8)
    time.sleep(delay)
    return random.random() < 0.3  # 30% accept, 70% decline

# 🚀 Main redistribution tab
def show_redistribution_tab(inventory_path):
    st.header("🔄 Smart Expiry-Based Redistribution")
    st.markdown("This agent proactively matches expiring products with nearby restaurants, hostels, NGOs, and B2B buyers using dynamic markdown pricing.")

    if "final_rows" not in st.session_state:
        st.session_state.final_rows = None
        st.session_state.unsold_skus = None

    if st.button("🚀 Run Redistribution Agent"):
        df, _ = run_redistribution(inventory_path)

        if df.empty:
            st.warning("No items expiring within the next 2 days.")
            return

        st.markdown("### 🤖 Agentic Outreach Simulation")

        final_rows = []
        stock_saved = 0
        unsold_skus = []

        for _, row in df.iterrows():
            st.markdown(f"#### 🟢 SKU {row['sku_id']} ({row['product']}) — Expiring on {row['expiry']} — Stock: {row['stock']}")
            top_buyers = rank_buyers_for_sku(row["zone"])[:3]
            accepted_buyer = None

            for buyer in top_buyers:
                with st.spinner(f"📨 Sending offer to {buyer['name']} via {buyer['channel']}..."):
                    accepted = simulate_buyer_response(buyer)

                icon_path = icon_map.get(buyer["channel"])
                img_html = ""
                if icon_path and os.path.exists(icon_path):
                    base64_icon = get_image_base64(icon_path)
                    img_html = f"<img src='data:image/png;base64,{base64_icon}' width='18' style='margin-left: 8px; vertical-align: middle;'/>"

                if accepted:
                    accepted_buyer = buyer
                    st.markdown(
                        f"✅ <b>{buyer['name']}</b> accepted the offer via {buyer['channel']} {img_html}",
                        unsafe_allow_html=True
                    )
                    break
                else:
                    st.markdown(
                        f"⚠️ No response from <i>{buyer['name']}</i> via {buyer['channel']} {img_html}",
                        unsafe_allow_html=True
                    )

            row_data = row.to_dict()
            if accepted_buyer:
                st.markdown(
                    f"**🧾 Finalized Deal**: SKU {row['sku_id']} routed to *{accepted_buyer['name']}* at **{row['new_price']}** (was {row['old_price']})"
                )
                row_data.update({
                    "buyer": accepted_buyer["name"],
                    "channel": accepted_buyer["channel"],
                    "status": "✅ Routed"
                })
                stock_saved += row["stock"]
            else:
                st.error("❗ No buyers responded. Item remains unsold.")
                row_data.update({
                    "buyer": "—",
                    "channel": "—",
                    "status": "❌ Unsold"
                })
                unsold_skus.append(row_data)

            final_rows.append(row_data)
            st.markdown("---")

        st.session_state.final_rows = final_rows
        st.session_state.unsold_skus = unsold_skus

    # Show results after routing simulation
    if st.session_state.final_rows:
        routed_count = sum(1 for r in st.session_state.final_rows if r['status'] == '✅ Routed')
        saved_count = sum(r['stock'] for r in st.session_state.final_rows if r['status'] == '✅ Routed')

        st.success(f"✅ {routed_count} items routed successfully!")
        st.metric("📦 Total Stock Saved", f"{saved_count} units")
        st.progress(min(saved_count / 100, 1.0))

        display_df = pd.DataFrame(st.session_state.final_rows)[[
            "sku_id", "product", "expiry", "zone", "buyer", "channel", "old_price", "new_price", "stock", "status"
        ]]
        st.markdown("### 📋 Final Redistribution Report")
        st.dataframe(display_df, use_container_width=True)

    # 🔁 Retry Logic Block
    if st.session_state.unsold_skus:
        st.markdown("## 🔁 Retry Unsold SKUs with Higher Discount")

        discount_options = [10, 20, 30, 40]
        selected_discount = st.selectbox("🔻 Choose Retry Discount Escalation", discount_options, index=0)

        if st.button("🔄 Retry with Selected Discount"):
            retry_results = []
            retry_saved = 0

            for sku in st.session_state.unsold_skus:
                original_price = float(str(sku["old_price"]).replace("₹", ""))
                current_price = float(str(sku["new_price"]).replace("₹", ""))
                current_discount_pct = round((1 - current_price / original_price) * 100)

                new_discount_pct = min(current_discount_pct + selected_discount, 90)
                new_price = round(original_price * (1 - new_discount_pct / 100), 2)
                sku["new_price"] = f"₹{new_price}"

                st.markdown(f"### 🟡 Retrying: {sku['sku_id']} ({sku['product']}) @ {sku['new_price']} ({new_discount_pct}% off)")
                top_buyers = rank_buyers_for_sku(sku["zone"])[:3]
                accepted = False

                for buyer in top_buyers:
                    with st.spinner(f"📨 Retrying with {buyer['name']} via {buyer['channel']}..."):
                        accepted = simulate_buyer_response(buyer)

                    if accepted:
                        st.success(f"✅ {buyer['name']} accepted the new offer at {sku['new_price']}")
                        sku["buyer"] = buyer["name"]
                        sku["channel"] = buyer["channel"]
                        sku["status"] = "✅ Routed"
                        retry_saved += sku["stock"]
                        retry_results.append(sku)
                        break
                    else:
                        st.warning(f"❌ No response from {buyer['name']}")

                if not accepted:
                    st.error("🚫 Still unsold.")
                    retry_results.append(sku)

            st.success(f"🎉 Retry Completed — Additional Stock Saved: {retry_saved} units")
            retry_df = pd.DataFrame(retry_results)[[
                "sku_id", "product", "expiry", "zone", "buyer", "channel", "old_price", "new_price", "stock", "status"
            ]]
            st.dataframe(retry_df, use_container_width=True)

# 📈 Agent Summary block
def show_agent_summary(df, buyer_stats, next_expiring_df):
    st.header("📊 Redistribution Summary")
    st.markdown(f"""
    - **SKUs flagged:** {len(df)}
    - **Matched Buyers:** {buyer_stats['matched']}
    - **Deals finalized:** {buyer_stats['accepted']}
    - **Unsold SKUs:** {buyer_stats['unsold']}
    - **Total stock saved:** {buyer_stats['stock_saved']} units
    """)
    st.markdown("---")
    st.markdown("### ⏳ Upcoming Expiries (Next 3–5 Days)")
    st.dataframe(next_expiring_df, use_container_width=True)
