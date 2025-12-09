# newdoordash_tracker_web.py — Now with Manual Entry + everything else
import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

DATA_FILE = "doordash_records.json"
MASTER_RESET_PASSWORD = "doordash2025"   # ← Change anytime

def load_records():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_records(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

def delete_all_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.session_state.records = []
    st.session_state.active_dash = None

# ────────────────── Init ──────────────────
st.set_page_config(page_title="DoorDash Tracker", page_icon="🚗", layout="centered")
st.title("🚗 DoorDash Driver Recordkeeping Pro")

if "active_dash" not in st.session_state:
    st.session_state.active_dash = None
if "records" not in st.session_state:
    st.session_state.records = load_records()

records = st.session_state.records

# ────────────────── MAIN DASHBOARD ──────────────────
col_live, col_manual = st.columns([2, 2])

with col_live:
    if st.session_state.active_dash is None:
        st.subheader("Live Dash")
        start_odo = st.number_input("Starting odometer (miles)", min_value=0.0, step=0.1, format="%.2f", key="live_odo")
        if st.button("Start Dash", type="primary", use_container_width=True):
            st.session_state.active_dash = {
                "start_time": datetime.now().isoformat(),
                "start_odo": float(start_odo),
                "expenses": 0.0,
                "notes": ""
            }
            st.success("
