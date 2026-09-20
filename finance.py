
import pandas as pd
from database import get_conn

def project_stats(project_id: int):
    conn = get_conn()
    proj = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not proj:
        conn.close()
        return {}
    expenses = pd.read_sql_query("SELECT * FROM expenses WHERE project_id=?", conn, params=(project_id,))
    payments = pd.read_sql_query("SELECT * FROM payments WHERE project_id=?", conn, params=(project_id,))
    variations = pd.read_sql_query("SELECT * FROM variations WHERE project_id=?", conn, params=(project_id,))
    worker_pays = pd.read_sql_query("SELECT * FROM worker_payments WHERE project_id=?", conn, params=(project_id,))
    conn.close()

    material_budget = proj["material_budget"] or 0
    labor_pct = proj["labor_pct"] or 40
    labor_budget = material_budget * labor_pct / 100.0
    transport_budget = proj["transport_budget"] or 0
    other_budget = proj["other_budget"] or 0
    rebate_pct = proj["rebate_pct"] if "rebate_pct" in proj.keys() and proj["rebate_pct"] is not None else 0
    # Budgeted rebate from hardware
    rebate_budget = material_budget * rebate_pct / 100.0
    # Effective material after rebate
    effective_material_budget = material_budget - rebate_budget
    total_budget = effective_material_budget + labor_budget + transport_budget + other_budget
    total_budget_without_rebate = material_budget + labor_budget + transport_budget + other_budget

    contract_value = proj["contract_value"] or 0

    approved_variations = variations[variations["status"]=="Approved"]["client_price"].sum() if not variations.empty else 0
    pending_variations = variations[variations["status"].isin(["Pending","Sent"])]["client_price"].sum() if not variations.empty else 0

    revenue = contract_value + approved_variations
    total_revenue_with_pending = revenue + pending_variations

    spent = expenses["amount"].sum() if not expenses.empty else 0
    # Avoid double counting: worker_payments are separate but also often logged as expense?
    # Rule: worker_payments are NOT added to expenses total if already categorized as Labor Pay? 
    # We treat worker_payments as authoritative labour cost, and if expenses has Labor Pay we use worker_payments instead to avoid double count
    labor_from_expenses = expenses[expenses["category"]=="Labor Pay"]["amount"].sum() if not expenses.empty else 0
    labor_from_worker = worker_pays["amount"].sum() if not worker_pays.empty else 0
    # If worker payments exist, use them as labor cost, not expense labor
    labor_actual = labor_from_worker if labor_from_worker>0 else labor_from_expenses

    material_actual = expenses[expenses["category"].isin(["Board/Melamine","Hardware & Runners","Quartz/Tops","Boards","Hardware","Material"]) ]["amount"].sum() if not expenses.empty else 0
    # Rebates actually received (category Rebate or negative hardware)
    transport_actual = expenses[expenses["category"].isin(["Transport/Fuel","Transport"])]["amount"].sum() if not expenses.empty else 0
    rebate_actual = expenses[expenses["category"].isin(["Rebate","Hardware Rebate","Cashback"])]["amount"].sum() if not expenses.empty else 0
    # rebate_actual is stored as positive income but we treat as cost reduction, so actual rebate value
    # If user logs rebate as negative expense, handle absolute
    other_actual = spent - material_actual - labor_from_expenses - transport_actual

    # For profit, total cost = spent - labor_from_expenses + labor_actual (replace)
    if labor_from_worker>0:
        total_cost = spent - labor_from_expenses + labor_from_worker
    else:
        total_cost = spent

    received = payments["amount"].sum() if not payments.empty else 0
    outstanding = revenue - received
    # Real cost includes rebate benefit: effective material = material_actual - rebate_actual
    # If rebate_actual logged as positive (income), subtract it from cost; if logged as negative, its sum is negative
    # Normalize: rebate income positive reduces cost
    rebate_effective_actual = abs(rebate_actual) if rebate_actual>0 else abs(rebate_actual)  
    # But if rebate logged as negative amount, material_actual already includes? Keep simple: total_cost already is spent, if rebate is negative, spent is lower
    # For profit, add budgeted rebate not yet received as projected profit, and actual rebate received boosts profit
    profit = revenue - total_cost + rebate_effective_actual + rebate_budget
    # For actual profit without projected rebate
    profit_actual_only = revenue - total_cost + rebate_effective_actual
    margin = (profit / revenue * 100) if revenue else 0

    unplanned = expenses[expenses["is_unplanned"]==1]["amount"].sum() if not expenses.empty else 0
    potentially_billable = expenses[(expenses["is_unplanned"]==1) & (expenses["billable_status"]=="Potentially Billable")]["amount"].sum() if not expenses.empty else 0
    billable = expenses[(expenses["is_unplanned"]==1) & (expenses["billable_status"]=="Billable")]["amount"].sum() if not expenses.empty else 0

    return {
        "material_budget": material_budget,
        "effective_material_budget": effective_material_budget,
        "labor_budget": labor_budget,
        "transport_budget": transport_budget,
        "other_budget": other_budget,
        "total_budget": total_budget,
        "total_budget_without_rebate": total_budget_without_rebate,
        "rebate_pct": rebate_pct,
        "rebate_budget": rebate_budget,
        "rebate_actual": rebate_effective_actual if 'rebate_effective_actual' in locals() else 0,
        "contract_value": contract_value,
        "approved_variations": approved_variations,
        "pending_variations": pending_variations,
        "revenue": revenue,
        "total_revenue_with_pending": total_revenue_with_pending,
        "spent": total_cost,
        "raw_spent": spent,
        "received": received,
        "outstanding": outstanding,
        "profit": profit,
        "margin": margin,
        "labor": labor_actual,
        "material": material_actual,
        "transport": transport_actual,
        "other": other_actual,
        "unplanned": unplanned,
        "potentially_billable": potentially_billable,
        "billable": billable,
        "labor_pct": labor_pct
    }

def company_stats():
    conn = get_conn()
    projects = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()
    rows=[]
    for _, r in projects.iterrows():
        s = project_stats(int(r["id"]))
        rows.append({
            "id": r["id"], "name": r["name"], "status": r["status"],
            "contract_value": r["contract_value"],
            **s
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return {"df": df, "total_contract":0,"total_revenue":0,"total_received":0,"total_outstanding":0,"total_spent":0,"total_profit":0,"avg_margin":0}
    return {
        "df": df,
        "total_contract": df["contract_value"].sum(),
        "total_revenue": df["revenue"].sum(),
        "total_received": df["received"].sum(),
        "total_outstanding": df["outstanding"].sum(),
        "total_spent": df["spent"].sum(),
        "total_profit": df["profit"].sum(),
        "avg_margin": df["margin"].mean()
    }
