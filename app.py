import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# 1. PERSISTENCE ENGINE (Auto-Save & Load)
# ==========================================
DB_FILE = "financial_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "projects": {
            "Waterkloof Kitchen": {
                "contract_value": 85000.0,
                "expenses": [
                    {"Date": "2026-09-10", "Category": "Board/Melamine", "Description": "6x White PG Bison Boards", "Amount": 6800.0},
                    {"Date": "2026-09-12", "Category": "Hardware", "Description": "Blum Soft-Close Slides", "Amount": 4200.0}
                ]
            }
        }
    }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session Data
if "db" not in st.session_state:
    st.session_state.db = load_data()

# ==========================================
# 2. PIN ACCESS CONTROL
# ==========================================
st.sidebar.title("🔒 Security Gatekeeper")
user_pin = st.sidebar.text_input("Enter 4-Digit PIN", type="password")

if user_pin != "1234":
    st.warning("⚠️ Access Restricted. Please enter the correct PIN in the sidebar to access financial panels.")
    st.info("💡 PIN Demo Code: **1234**")
    st.stop()

st.sidebar.success("🟢 System Unlocked")

# ==========================================
# 3. PROJECT SELECTOR & MANAGEMENT
# ==========================================
projects = list(st.session_state.db["projects"].keys())
selected_project = st.sidebar.selectbox("Active Project", projects)

# Project Header
st.title("📊 Nova Vital Financial OS")
st.subheader(f"Active Job: {selected_project}")

proj_data = st.session_state.db["projects"][selected_project]
contract_val = proj_data["contract_value"]

# Calculate Expenses
expenses = proj_data["expenses"]
total_spent = sum(e["Amount"] for e in expenses)
remaining = contract_val - total_spent
drain_pct = min((total_spent / contract_val) if contract_val > 0 else 0.0, 1.0)

# ==========================================
# 4. REAL-TIME METRICS & DRAIN INDICATOR
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Contract Value", f"R {contract_val:,.2f}")
col2.metric("Total Spent", f"R {total_spent:,.2f}", delta=f"-R {total_spent:,.2f}", delta_color="inverse")
col3.metric("Budget Remaining", f"R {remaining:,.2f}", delta=f"R {remaining:,.2f}")

st.write("**Budget Drain Progress**")
st.progress(drain_pct)
st.caption(f"{drain_pct*100:.1f}% of total project budget spent.")

st.divider()

# ==========================================
# 5. REAL-TIME DAILY EXPENSE LOGGER
# ==========================================
st.subheader("➕ Log Daily Expense (Real-Time Drain Tracker)")

with st.form("add_expense_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    exp_date = col_a.date_input("Date", datetime.now())
    exp_cat = col_b.selectbox("Category", ["Board/Melamine", "Hardware & Runners", "Quartz/Tops", "Labor Pay", "Transport/Fuel", "Sundries"])
    
    col_c, col_d = st.columns([2, 1])
    exp_desc = col_c.text_input("Description / Item Notes")
    exp_amount = col_d.number_input("Amount (ZAR)", min_value=0.0, step=100.0)
    
    submitted = st.form_submit_button("➕ Add Expense to Project")
    if submitted and exp_amount > 0:
        new_entry = {
            "Date": str(exp_date),
            "Category": exp_cat,
            "Description": exp_desc,
            "Amount": float(exp_amount)
        }
        st.session_state.db["projects"][selected_project]["expenses"].append(new_entry)
        save_data(st.session_state.db)
        st.success("Expense logged & saved to database!")
        st.rerun()

# ==========================================
# 6. EXPENSE LEDGER TABLE
# ==========================================
st.subheader("📋 Real-Time Expense Ledger")
if expenses:
    df = pd.DataFrame(expenses)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No expenses logged yet for this project.")
