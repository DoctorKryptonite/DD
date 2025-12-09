# doordash_tracker_web.py  —  Upgraded version with full history + CSV export
import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

DATA_FILE = "doordash_records.json"

# ------------------- Data functions -------------------
def load_records():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_records(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

# ------------------- Initialize -------------------
st.set_page_config(page_title="DoorDash Tracker", page_icon="🚗", layout="centered")
st.title("🚗 DoorDash Driver Recordkeeping Pro")

if "active_dash" not in st.session_state:
    st.session_state.active_dash = None
if "records" not in st.session_state:
    st.session_state.records = load_records()

records = st.session_state.records

# ------------------- Main Dashboard -------------------
if st.session_state.active_dash is None:
    st.subheader("Start New Dash")
    start_odo = st.number_input("Starting odometer (miles)", min_value=0.0, step=0.1, format="%.2f")
    col1, col2 = st.columns(2)
    if col1.button("Start Dash", type="primary", use_container_width=True):
        if start_odo >= 0:
            st.session_state.active_dash = {
                "start_time": datetime.now().isoformat(),
                "start_odo": float(start_odo),
                "expenses": 0.0,
                "notes": ""
            }
            st.success(f"Dash started at {datetime.now():%H:%M:%S}")
            st.rerun()

else:
    start_dt = datetime.fromisoformat(st.session_state.active_dash["start_time"])
    st.success(f"Active – Started {start_dt:%H:%M}  |  {st.session_state.active_dash['start_odo']} mi")

    # Add expense during dash
    c1, c2 = st.columns(2)
    exp_amt = c1.number_input("Expense ($)", min_value=0.0, step=0.01, key="e1")
    exp_note = c2.text_input("Note (optional)", key="e2")
    if st.button("Add Expense", use_container_width=True):
        if exp_amt > 0:
            st.session_state.active_dash["expenses"] += exp_amt
            if exp_note:
                st.session_state.active_dash["notes"] += ("\n" if st.session_state.active_dash["notes"] else "") + f"• ${exp_amt:.2f} – {exp_note}"
            st.success(f"${exp_amt:.2f} added")
            st.rerun()

    st.divider()
    st.subheader("Finish Dash")
    col_a, col_b = st.columns(2)
    end_odo = col_a.number_input("Ending odometer (miles)", min_value=0.0, step=0.1)
    earnings = col_b.number_input("Total earnings ($)", min_value=0.0, step=0.01)
    final_exp = st.number_input("Final expense (optional) ($)", min_value=0.0, step=0.01)

    if st.button("Complete Dash & Save", type="primary", use_container_width=True):
        if end_odo < st.session_state.active_dash["start_odo"]:
            st.error("Ending mileage cannot be lower than starting")
        else:
            st.session_state.active_dash["expenses"] += final_exp
            end_time = datetime.now()
            duration = (end_time - start_dt).total_seconds() / 3600
            miles = end_odo - st.session_state.active_dash["start_odo"]
            net = earnings - st.session_state.active_dash["expenses"]
            hourly = net / duration if duration > 0 else 0

            new_record = {
                "date": start_dt.strftime("%Y-%m-%d"),
                "start_time": start_dt.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "duration_hours": round(duration, 2),
                "miles": round(miles, 2),
                "gross_earnings": round(earnings, 2),
                "expenses": round(st.session_state.active_dash["expenses"], 2),
                "net_profit": round(net, 2),
                "hourly_rate": round(hourly, 2),
                "notes": st.session_state.active_dash["notes"]
            }

            records.append(new_record)
            save_records(records)
            st.session_state.records = records
            st.session_state.active_dash = None
            st.balloons()
            st.success(f"Net profit ${net:.2f}  →  ${hourly:.2f}/h")
            st.rerun()

# ------------------- Full Records & Export Page -------------------
st.divider()
st.subheader("Full History & Export")

if not records:
    st.info("No dashes recorded yet. Complete your first dash to see data here.")
else:
    df = pd.DataFrame(records)
    df = df.sort_values("date", ascending=False)

    # Lifetime totals
    total_miles = df["miles"].sum()
    total_earnings = df["gross_earnings"].sum()
    total_expenses = df["expenses"].sum()
    total_net = df["net_profit"].sum()
    total_hours = df["duration_hours"].sum()
    avg_hourly = total_net / total_hours if total_hours > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lifetime Miles", f"{total_miles:,.1f}")
    col2.metric("Gross Earnings", f"${total_earnings:,.2f}")
    col3.metric("Total Net Profit", f"${total_net:,.2f}")
    col4.metric("Average Hourly", f"${avg_hourly:.2f}")

    # Search / filter
    search = st.text_input("Search date (YYYY-MM-DD) or leave blank for all")
    if search:
        df = df[df["date"].str.contains(search) | df["notes"].str.contains(search, na=False)]

    st.dataframe(df.drop(columns=["notes"]), use_container_width=True, hide_index=True)

    # Download buttons
    csv = df.to_csv(index=False).encode()
    st.download_button(
        label="📥 Download Full Records as CSV (for taxes/Excel)",
        data=csv,
        file_name=f"DoorDash_Records_{datetime.now():%Y-%m-%d}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ------------------- Upgrade Instructions (always visible) -------------------
with st.expander("ℹ️ How to upgrade or keep this app forever", expanded=False):
    st.markdown("""
    **This app is 100 % free forever on Streamlit Community Cloud.**

    If you ever want:
    - Private app (nobody else can see your data URL)
    - More than 1 private app
    - Faster performance or custom domain

    → Just go to https://share.streamlit.io → click your profile → Upgrade (starts at ~$9/month).

    You can stay on the free plan forever with no limits on public usage.
    """)

# ------------------- Sidebar recent dashes -------------------
with st.sidebar:
    st.header("Recent Dashes")
    for r in records[-8:][::-1]:
        st.write(f"**{r['date']}**")
        st.caption(f"{r['duration_hours']} h  •  ${r['net_profit']:.2f} net  •  ${r['hourly_rate']:.2f}/h")
        st.divider()
