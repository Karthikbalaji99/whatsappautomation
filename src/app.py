import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
from mock_api_client import MockAPIClient
from logger import ExcelLogger

# Page configuration
st.set_page_config(
    page_title="WhatsApp Campaign Manager (Mock API)",
    page_icon="📱",
    layout="wide"
)

# Initialize session state (to track campaign state and results)
if "campaign_running" not in st.session_state:
    st.session_state.campaign_running = False
if "results" not in st.session_state:
    st.session_state.results = []

# Load message templates [(this is a mock, so we use a local JSON file) later we will use an assitant to generate the templates based on the user profile and interaction]
@st.cache_data
def load_templates():
    template_path = "templates/message_templates.json"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # If file missing, fallback to an empty dict
        return {}

# Load leads data [(currently from a CSV file) - later we will use a database or an API]]
@st.cache_data
def load_leads():
    leads_path = "data/leads.csv"
    if os.path.exists(leads_path):
        return pd.read_csv(leads_path, encoding="utf-8", dtype={"phone": str})
    else:
        st.error(f"Leads file not found at {leads_path}")
        return pd.DataFrame()

# Initialize mock API client and Excel logger
mock_api = MockAPIClient()
excel_logger = ExcelLogger()

# Start background monitoring if connected
if mock_api.is_connected:
    excel_logger.start_status_monitoring(mock_api)

# Main UI
st.title("📱 WhatsApp Campaign Manager (Mock API)")
st.markdown("### BorderPlus - Automated Lead Outreach (Using Mock Endpoints)")

# Two‐column layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Campaign Control")

    # Connection status
    if mock_api.is_connected:
        st.success("✅ Mock API Connected")
    else:
        st.error("❌ Mock API Not Connected")
        st.info("Start `uvicorn src.mock_api_server:app --port 8000` and reload.")

    # Load and preview leads
    leads_df = load_leads()
    if not leads_df.empty:
        st.success(f"📊 {len(leads_df)} leads loaded")
        with st.expander("Preview Leads"):
            st.dataframe(leads_df)

        # Send Campaign button
        if st.button(
            "🚀 Send WhatsApp Campaign",
            disabled=not mock_api.is_connected or st.session_state.campaign_running,
            use_container_width=True,
        ):
            st.session_state.campaign_running = True
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Convert to list of dicts and load templates
            leads_data = leads_df.to_dict("records")
            templates = load_templates()

            status_text.text("Sending messages via Mock API...")

            # Send in bulk
            results = mock_api.send_bulk_messages(leads_data, templates)

            # Log results
            excel_logger.log_message_batch(results)

            # Update session state
            st.session_state.results = results
            st.session_state.campaign_running = False

            progress_bar.progress(100)
            status_text.text("Campaign dispatched (mock)!")
            success_count = sum(1 for r in results if r["status"] == "queued")
            st.success(f"✅ {success_count}/{len(results)} messages queued (mock)")
            time.sleep(2)
            st.rerun()
    else:
        st.warning("No leads data found. Please check data/leads.csv")

with col2:
    st.subheader("📊 Real‐time Delivery & Reply Status")

    # Auto‐refresh toggle
    auto_refresh = st.checkbox("Auto‐refresh (every 10 seconds)", value=True)

    # Control buttons: Refresh / Retry / Follow‐up
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🔄 Refresh Status"):
            st.rerun()
    with b2:
        if st.button("🔄 Retry Failed Now"):
            current_time = datetime.now()
            excel_logger.retry_failed_messages(mock_api, current_time)
            st.success("Retry attempt completed!")
            time.sleep(1)
            st.rerun()
    with b3:
        if st.button("📞 Send Follow‐ups"):
            current_time = datetime.now()
            excel_logger.send_followups(mock_api, current_time)
            st.success("Follow‐up check completed!")
            time.sleep(1)
            st.rerun()

    

    # Display current data
    current_data = excel_logger.get_current_data()
    if not current_data.empty:
        # Metrics
        colm = st.columns(5)
        with colm[0]:
            delivered = len(current_data[current_data["Delivery_Status"] == "sent"])
            st.metric("✅ Delivered", delivered)
        with colm[1]:
            failed = len(current_data[current_data["Delivery_Status"] == "failed"])
            st.metric("❌ Failed", failed)
        with colm[2]:
            queued = len(current_data[current_data["Delivery_Status"] == "queued"])
            st.metric("⏳ Queued", queued)
        with colm[3]:
            replied = current_data["Reply_History"].apply(
                lambda x: len(json.loads(x)) if pd.notna(x) and x != "" else 0
            ).sum()
            st.metric("💬 Replies", replied)
        with colm[4]:
            followups = len(current_data[current_data["Follow_Up_Status"] == "sent"])
            st.metric("📞 Follow‐ups Sent", followups)

        st.markdown("### Detailed Status")
        def highlight_status(row):
            if row["Delivery_Status"] == "sent":
                return ["background-color: #d4edda"] * len(row)
            elif row["Delivery_Status"] == "failed":
                return ["background-color: #f8d7da"] * len(row)
            elif row["Delivery_Status"] == "queued":
                return ["background-color: #fff3cd"] * len(row)
            else:
                return [""] * len(row)

        display_cols = [
            "Name", "Phone", "Delivery_Status", "Reply_History",
            "Retry_Count", "Follow_Up_Status", "Message_Sent_Time", "Last_Updated"
        ]
        available = [c for c in display_cols if c in current_data.columns]
        disp_df = current_data[available]
        styled = disp_df.style.apply(highlight_status, axis=1)
        st.dataframe(styled, use_container_width=True)

        with st.expander("📋 View All Columns"):
            st.dataframe(current_data, use_container_width=True)

        # Download full log
        with open(excel_logger.log_file_path, "rb") as f:
            st.download_button(
                label="📥 Download Full Log (Excel)",
                data=f.read(),
                file_name="delivery_log.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No campaign data yet. Send a campaign to see status.")

    # Auto‐refresh
    if auto_refresh and not st.session_state.campaign_running:
        time.sleep(10)
        st.rerun()
