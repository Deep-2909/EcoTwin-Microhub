import streamlit as st
from agents.expiry_agent import run_expiry_agent

def show_agent_logs(inventory_path):
    st.header("🧠 Expiry Agent Logs")
    if st.button("Run Expiry Agent"):
        _, logs = run_expiry_agent(inventory_path)
        for log in logs:
            st.success(log)
    else:
        st.info("Click the button above to run the agent.")
