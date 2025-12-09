import streamlit as st
import json
import os
from datetime import datetime
from tkinter import simpledialog  # Note: For mobile, we'll use Streamlit inputs instead

DATA_FILE = "doordash_records.json"

# Load records
@st.cache_data
def load_records():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# Save records
def save_records(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

st.set_page_config(page_title="DoorDash Tracker", page_icon="🚗", layout="wide")

st.title("🚗 DoorDash Driver Recordkeeping")

# Session state for active dash
if "active_dash" not in st.session_state:
    st.session_state.active_dash = None
if "all_records" not in st.session_state:
    st.session_state.all_records = load_records()

# Main interface
col1, col2 = st.columns([1, 3])

with col1:
    if st.session_state.active_dash is None:
        if st.button("Start Dash", type="primary", use_container_width=True):
            start_odo = st.number_input("Starting Odometer (miles):", min_value=0.0, format="%.2f")
            if st.button("Confirm Start"):
                if start_odo >= 0:
                    st.session_state.active_dash = {
                        "start_time": datetime.now().isoformat(),
                        "start_odo": start_odo,
                        "expenses": 0.0,
                        "notes": ""
                    }
                    st.rerun()
                else:
                    st.error("Please enter a valid odometer reading.")
    else:
        st.info(f"Active Dash Started: {datetime.fromisoformat(st.session_state.active_dash['start_time']).strftime('%H:%M:%S')}")
        st.info(f"Start Odometer: {st.session_state.active_dash['start_odo']} mi")
        expense_amt = st.number_input("Add Expense ($):", min_value=0.0, format="%.2f")
        expense_note = st.text_input("Expense Note (optional):")
        if st.button("Add Expense"):
            if expense_amt > 0:
                st.session_state.active_dash["expenses"] += expense_amt
                if expense_note:
                    st.session_state.active_dash["notes"] += ("" if not st.session_state.active_dash["notes"] else "\n") + f"- ${expense_amt}: {expense_note}"
                st.success(f"${expense_amt} added.")
                st.rerun()

        if st.button("End Dash", type="secondary", use_container_width=True):
            end_odo = st.number_input("Ending Odometer (miles):", min_value=0.0, format="%.2f")
            earnings = st.number_input("Total Earnings ($):", min_value=0.0, format="%.2f")
            final_expense = st.number_input("Final Expense (optional, $):", min_value=0.0, format="%.2f")
            if st.button("Confirm End"):
                if end_odo >= 0 and earnings >= 0:
                    st.session_state.active_dash["expenses"] += final_expense
                    start_time = datetime.fromisoformat(st.session_state.active_dash["start_time"])
                    end_time = datetime.now()
                    duration_hours = (end_time - start_time).total_seconds() / 3600
                    miles_driven = end_odo - st.session_state.active_dash["start_odo"]
                    net_profit = earnings - st.session_state.active_dash["expenses"]
                    hourly = net_profit / duration_hours if duration_hours > 0 else 0

                    record = {
                        "date": start_time.strftime("%Y-%m-%d"),
                        "start_time": start_time.strftime("%H:%M"),
                        "end_time": end_time.strftime("%H:%M"),
                        "duration_hours": round(duration_hours, 2),
                        "start_odo": st.session_state.active_dash["start_odo"],
                        "end_odo": end_odo,
                        "miles": round(miles_driven, 2),
                        "gross_earnings": earnings,
                        "expenses": round(st.session_state.active_dash["expenses"], 2),
                        "net_profit": round(net_profit, 2),
                        "hourly_rate": round(hourly, 2),
                        "notes": st.session_state.active_dash["notes"]
                    }

                    st.session_state.all_records.append(record)
                    save_records(st.session_state.all_records)
                    st.session_state.active_dash = None

                    # Summary
                    summary = f"""
                    **DOORDASH SUMMARY**
                    - **Date**: {record['date']}
                    - **Time**: {record['start_time']} – {record['end_time']}
                    - **Duration**: {record['duration_hours']} hours
                    - **Miles Driven**: {record['miles']} mi
                    - **Gross Earnings**: ${record['gross_earnings']:.2f}
                    - **Expenses**: ${record['expenses']:.2f}
                    - **Net Profit**: ${record['net_profit']:.2f}
                    - **Pay per Hour**: ${record['hourly_rate']:.2f}
                    """
                    st.success(summary)
                    st.rerun()
                else:
                    st.error("Please enter valid values.")

# Past records sidebar
with st.sidebar:
    st.header("Past Dashes")
    records_df = st.dataframe(
        [{"Date": r["date"], "Duration (h)": r["duration_hours"], "Net Profit": f"$$ {r['net_profit']:.2f}", "Hourly": f" $${r['hourly_rate']:.2f}"} 
         for r in st.session_state.all_records[-10:][::-1]],  # Last 10, reversed for recent first
        use_container_width=True
    )