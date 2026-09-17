import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Nova Vital Financial OS",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Financial Operating System (OS)")
st.caption("Nova Vital Realty - Master Income, Project Margins, Daily Cash Velocity & Automated Variation Order Engine")

# --- INITIALIZE SESSION STATE ---
if "daily_logs" not in st.session_state:
    st.session_state.daily_logs = []
if "vo_counter" not in st.session_state:
    st.session_state.vo_counter = 1

# ==========================================
# PDF VARIATION ORDER GENERATOR FUNCTION
# ==========================================
def generate_vo_pdf(vo_number, project_name, client_name, item_desc, net_cost, markup_percent=15):
    markup_amount = net_cost * (markup_percent / 100)
    total_due = net_cost + markup_amount

    pdf = FPDF()
    pdf.add_page()
    
    # Company Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "NOVA VITAL REALTY", ln=True, align="L")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Joinery, Custom Cabinetry & Interior Renovations", ln=True, align="L")
    pdf.cell(0, 5, "Pretoria, South Africa", ln=True, align="L")
    pdf.ln(10)
    
    # Document Title Box
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, f"VARIATION ORDER: {vo_number}", ln=True, fill=True, align="C")
    pdf.ln(5)
    
    # Project & Date Information
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(100, 6, f"Project: {project_name}", ln=False)
    pdf.cell(0, 6, f"Date: {datetime.now().strftime('%d %b %Y')}", ln=True)
    pdf.cell(100, 6, f"Client Name: {client_name}", ln=True)
    pdf.ln(10)
    
    # Legal Scope Notice
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, "Notice of Scope Change: The following unbudgeted material/labor request falls outside the original Bill of Quantities (BOQ). Work will proceed upon sign-off/payment.")
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(110, 8, "Description of Unbudgeted Item/Labor", border=1, fill=True)
    pdf.cell(40, 8, "Cost (ZAR)", border=1, fill=True, align="R")
    pdf.cell(40, 8, f"Total + {markup_percent}% Markup", border=1, fill=True, align="R")
    pdf.ln()
    
    # Table Content
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(110, 8, str(item_desc), border=1)
    pdf.cell(40, 8, f"R {net_cost:,.2f}", border=1, align="R")
    pdf.cell(40, 8, f"R {total_due:,.2f}", border=1, align="R")
    pdf.ln(12)
    
    # Total Calculation
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(150, 8, "TOTAL VARIATION DUE:", align="R")
    pdf.cell(40, 8, f"R {total_due:,.2f}", border=1, align="R")
    pdf.ln(20)
    
    # Signatures Block
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(90, 6, "Contractor Signature: __________________", ln=False)
    pdf.cell(0, 6, "Client Acceptance: __________________", ln=True)
    
    return bytes(pdf.output())

# ==========================================
# PANEL 1: MONTHLY EXPECTED INCOME & FIXED BILLS
# ==========================================
st.header("1. Monthly Master Income & Fixed Bills")

col_inc1, col_inc2 = st.columns(2)
with col_inc1:
    monthly_draw = st.number_input("Monthly Owner's Salary / Personal Draw (R)", value=35000, step=1000)

with col_inc2:
    rent = st.number_input("Rent / Housing (R)", value=12000, step=500)
    groceries = st.number_input("Monthly Groceries (R)", value=6000, step=250)
    electricity = st.number_input("Electricity & Power (R)", value=2500, step=100)
    wifi = st.number_input("WiFi & Connectivity (R)", value=850, step=50)

total_fixed_bills = rent + groceries + electricity + wifi
net_after_bills = monthly_draw - total_fixed_bills

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total Owner Draw", f"R {monthly_draw:,.2f}")
col_m2.metric("Total Fixed Bills", f"R {total_fixed_bills:,.2f}")
col_m3.metric("Net Surplus Buffer", f"R {net_after_bills:,.2f}")

st.divider()

# ==========================================
# PANEL 2: DEDICATED PROJECT FINANCE MANAGEMENT
# ==========================================
st.header("2. Project Finance Management Panel")

col_p1, col_p2 = st.columns(2)
with col_p1:
    project_name = st.text_input("Active Project Name / Site", value="Kolgans St Kitchen Refit")
    client_name = st.text_input("Client Name", value="Client Ref - Kolgans")
    material_cost = st.number_input("Raw Material Cost (BOQ) (R)", value=18000, step=500)
    labor_charge_client = st.number_input("Labor Charge Invoiced to Client (R)", value=15000, step=500)

with col_p2:
    actual_subcontractor_labor = st.number_input("Actual Labor Paid Out (R)", value=9000, step=500)
    supplier_kickback = st.number_input("Supplier Rebate / Kickback Received (R)", value=1200, step=100)
    project_overhead = st.number_input("Transport & Consumables Overhead (R)", value=3500, step=250)

net_material_outlay = max(0.0, material_cost - supplier_kickback)
gross_project_revenue = material_cost + labor_charge_client
total_project_outflow = net_material_outlay + actual_subcontractor_labor + project_overhead
net_project_profit = gross_project_revenue - total_project_outflow

col_proj1, col_proj2, col_proj3 = st.columns(3)
col_proj1.metric("Gross Project Revenue", f"R {gross_project_revenue:,.2f}")
col_proj2.metric("Net Outlay (After Kickback)", f"R {net_material_outlay:,.2f}")
col_proj3.metric("Net Project Profit", f"R {net_project_profit:,.2f}")

st.divider()

# ==========================================
# PANEL 3 & 4: EVENING LOGINS & AUTOMATED VO GENERATOR
# ==========================================
st.header("3 & 4. Evening Log-In & Automated Variation Order Engine")

daily_baseline_cap = st.number_input("Target Daily Personal Allowance (R/day)", value=300, step=50)

with st.form("evening_waste_log_form"):
    col_l1, col_l2, col_l3 = st.columns(3)
    
    with col_l1:
        proj_unbudgeted_spend = st.number_input("Unbudgeted Material/Site Spend Today (R)", value=0.0, step=50.0)
        proj_spend_note = st.text_input("Unbudgeted Item Details", value="Extra aluminum trim & specialized screws")
        
    with col_l2:
        pers_essentials = st.number_input("Personal Essentials Spent (R)", value=0.0, step=10.0)
        pers_discretionary = st.number_input("Personal Discretionary Spent (R)", value=0.0, step=10.0)
        
    with col_l3:
        st.write("**Leak Check Flags**")
        leak_m = st.checkbox("[M] Unbilled Material/Hardware Run")
        leak_t = st.checkbox("[T] Unplanned Fuel/Supplier Trip")
        leak_p = st.checkbox("[P] Unreceipted Cash Drift")

    submit_log = st.form_submit_button("Submit Evening Log & Audit")

if submit_log:
    leak_flags = [f for f, checked in [("M", leak_m), ("T", leak_t), ("P", leak_p)] if checked]
    overspend = pers_discretionary - daily_baseline_cap
    tomorrow_cap = max(0.0, daily_baseline_cap - overspend)
    
    status_code = "🟢 GREEN" if not leak_flags and overspend <= 0 else ("🟡 AMBER" if len(leak_flags) <= 1 else "🔴 RED BREACH")
    
    audit_msg = f"**Status: {status_code}** | Spent: R{pers_discretionary:,.2f} | Tomorrow Cap: R{tomorrow_cap:,.2f}\n\n"
    if leak_m:
        audit_msg += f"👉 **[M] Material Leak Detected (R{proj_unbudgeted_spend:,.2f}):** Unbilled materials logged. Generate VO below to recover costs.\n"
    if leak_t:
        audit_msg += "👉 **[T] Transport Leak:** Consolidate site runs tomorrow.\n"
    if leak_p:
        audit_msg += "👉 **[P] Cash Drift:** Unreceipted personal cash draw flagged.\n"

    st.session_state.daily_logs.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Unbudgeted Spend": proj_unbudgeted_spend,
        "Spend Note": proj_spend_note,
        "Discretionary": pers_discretionary,
        "Leaks": "/".join(leak_flags) if leak_flags else "None",
        "Status": status_code,
        "Audit": audit_msg
    })

# --- RENDER AUDIT & PDF GENERATOR BUTTON ---
if st.session_state.daily_logs:
    latest = st.session_state.daily_logs[-1]
    
    st.subheader("📊 Latest Evening Audit Output")
    if "🟢" in latest["Status"]:
        st.success(latest["Audit"])
    elif "🟡" in latest["Status"]:
        st.warning(latest["Audit"])
    else:
        st.error(latest["Audit"])

    # AUTOMATED VO GENERATOR SECTION
    if "M" in latest["Leaks"] and latest["Unbudgeted Spend"] > 0:
        st.subheader("📄 Automated Variation Order (VO) Generator")
        st.info("A material leak was detected. Generate and download a legal Variation Order PDF to bill the client.")
        
        vo_id = f"VO-{st.session_state.vo_counter:03d}"
        
        col_vo1, col_vo2 = st.columns(2)
        with col_vo1:
            vo_markup = st.slider("Select Markup % to apply to client", min_value=0, max_value=30, value=15)
        
        pdf_bytes = generate_vo_pdf(
            vo_number=vo_id,
            project_name=project_name,
            client_name=client_name,
            item_desc=latest["Spend Note"],
            net_cost=latest["Unbudgeted Spend"],
            markup_percent=vo_markup
        )
        
        st.download_button(
            label=f"📥 Download {vo_id} PDF Invoice (R {latest['Unbudgeted Spend'] * (1 + vo_markup/100):,.2f})",
            data=pdf_bytes,
            file_name=f"{vo_id}_{project_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
