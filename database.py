
import sqlite3, os, json, shutil
from datetime import datetime
from pathlib import Path

DB_FILE = os.getenv("NOVA_DB", "nova_vital.db")
JSON_LEGACY = "financial_db.json"

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        company TEXT,
        notes TEXT,
        created_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        client_id INTEGER,
        client_name TEXT,
        client_phone TEXT,
        client_email TEXT,
        address TEXT,
        start_date TEXT,
        due_date TEXT,
        material_budget REAL DEFAULT 0,
        labor_pct REAL DEFAULT 40,
        transport_budget REAL DEFAULT 0,
        other_budget REAL DEFAULT 0,
        markup_pct REAL DEFAULT 25,
        rebate_pct REAL DEFAULT 0,
        rebate_value REAL DEFAULT 0,
        labor_auto_calc INTEGER DEFAULT 1,
        contract_value REAL DEFAULT 0,
        status TEXT DEFAULT 'Active',
        notes TEXT DEFAULT '',
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        expense_date TEXT,
        category TEXT,
        description TEXT,
        amount REAL,
        supplier TEXT DEFAULT '',
        worker TEXT DEFAULT '',
        receipt_ref TEXT DEFAULT '',
        is_unplanned INTEGER DEFAULT 0,
        billable_status TEXT DEFAULT 'Non-Billable',
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        payment_date TEXT,
        description TEXT,
        amount REAL,
        payment_type TEXT DEFAULT 'Progress Payment',
        method TEXT DEFAULT 'EFT',
        reference TEXT DEFAULT '',
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS variations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        variation_no TEXT UNIQUE,
        variation_date TEXT,
        description TEXT,
        material_cost REAL DEFAULT 0,
        labor_cost REAL DEFAULT 0,
        transport_cost REAL DEFAULT 0,
        other_cost REAL DEFAULT 0,
        markup_pct REAL DEFAULT 25,
        client_price REAL DEFAULT 0,
        cost_price REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS procurement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        item TEXT,
        quantity REAL DEFAULT 1,
        unit TEXT DEFAULT 'pcs',
        supplier TEXT DEFAULT '',
        quoted_price REAL DEFAULT 0,
        actual_price REAL DEFAULT 0,
        ordered INTEGER DEFAULT 0,
        received INTEGER DEFAULT 0,
        expected_date TEXT,
        status TEXT DEFAULT 'Required',
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        phone TEXT DEFAULT '',
        role TEXT DEFAULT 'Installer',
        default_rate REAL DEFAULT 0,
        skill_level TEXT DEFAULT 'Medium',
        is_active INTEGER DEFAULT 1,
        notes TEXT DEFAULT '',
        created_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS worker_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        worker_id INTEGER NOT NULL,
        payment_date TEXT,
        days REAL DEFAULT 0,
        rate REAL DEFAULT 0,
        amount REAL DEFAULT 0,
        description TEXT DEFAULT '',
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY(worker_id) REFERENCES workers(id)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        title TEXT,
        due_date TEXT,
        assigned_to TEXT DEFAULT '',
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Pending',
        progress INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS snags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        description TEXT,
        priority TEXT DEFAULT 'Medium',
        assigned_to TEXT DEFAULT '',
        due_date TEXT,
        status TEXT DEFAULT 'Open',
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS site_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        log_date TEXT,
        workers TEXT,
        arrival TEXT DEFAULT '',
        departure TEXT DEFAULT '',
        work_done TEXT,
        materials_used TEXT,
        issues TEXT,
        client_instructions TEXT DEFAULT '',
        weather TEXT DEFAULT '',
        notes TEXT,
        created_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT UNIQUE,
        category TEXT,
        quantity REAL DEFAULT 0,
        unit TEXT DEFAULT 'pcs',
        reorder_level REAL DEFAULT 5,
        unit_cost REAL DEFAULT 0,
        supplier TEXT DEFAULT '',
        location TEXT DEFAULT 'Workshop',
        created_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS inventory_moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inventory_id INTEGER,
        move_date TEXT,
        qty_change REAL,
        reason TEXT,
        project_id INTEGER,
        created_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        company TEXT DEFAULT '',
        phone TEXT,
        email TEXT DEFAULT '',
        source TEXT DEFAULT 'Referral',
        project_type TEXT DEFAULT '',
        estimated_value REAL DEFAULT 0,
        status TEXT DEFAULT 'New',
        notes TEXT DEFAULT '',
        created_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote_no TEXT UNIQUE,
        project_id INTEGER,
        client_id INTEGER,
        client_name TEXT,
        client_phone TEXT,
        address TEXT,
        description TEXT,
        subtotal REAL DEFAULT 0,
        labor_total REAL DEFAULT 0,
        transport_total REAL DEFAULT 0,
        markup_pct REAL DEFAULT 25,
        markup_value REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        vat_pct REAL DEFAULT 0,
        vat_value REAL DEFAULT 0,
        total REAL DEFAULT 0,
        valid_until TEXT,
        status TEXT DEFAULT 'Draft',
        terms TEXT DEFAULT '',
        created_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS quote_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote_id INTEGER,
        description TEXT,
        qty REAL DEFAULT 1,
        unit TEXT DEFAULT 'pcs',
        unit_price REAL DEFAULT 0,
        line_total REAL DEFAULT 0,
        FOREIGN KEY(quote_id) REFERENCES quotes(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT UNIQUE,
        project_id INTEGER,
        client_id INTEGER,
        client_name TEXT,
        invoice_date TEXT,
        due_date TEXT,
        description TEXT,
        subtotal REAL DEFAULT 0,
        vat_pct REAL DEFAULT 0,
        vat_value REAL DEFAULT 0,
        total REAL DEFAULT 0,
        amount_paid REAL DEFAULT 0,
        balance_due REAL DEFAULT 0,
        status TEXT DEFAULT 'Not Paid',
        bank_details TEXT DEFAULT '',
        created_at TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        description TEXT,
        qty REAL DEFAULT 1,
        unit_price REAL DEFAULT 0,
        line_total REAL DEFAULT 0,
        FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        action TEXT,
        entity TEXT,
        entity_id TEXT,
        details TEXT,
        user TEXT DEFAULT 'owner'
    )""")


    # --- MIGRATION FOR PRICING AUTOMATION (labor 40% + rebates) ---
    for col, typ in [("rebate_pct","REAL DEFAULT 0"), ("rebate_value","REAL DEFAULT 0"), ("labor_auto_calc","INTEGER DEFAULT 1")]:
        try:
            cur.execute(f"ALTER TABLE projects ADD COLUMN {col} {typ}")
        except Exception:
            pass

    conn.commit()
    conn.close()
    # Attempt migration
    try:
        migrate_json_if_exists()
    except Exception as e:
        print(f"Migration skipped: {e}")

def migrate_json_if_exists():
    if not os.path.exists(JSON_LEGACY):
        return
    if os.path.getsize(JSON_LEGACY) == 0:
        return
    backup = f"{JSON_LEGACY}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(JSON_LEGACY, backup)
    with open(JSON_LEGACY, "r") as f:
        data = json.load(f)
    conn = get_conn()
    cur = conn.cursor()
    existing = {r[0] for r in cur.execute("SELECT name FROM projects").fetchall()}
    for proj_name, pdata in data.get("projects", {}).items():
        if proj_name in existing:
            continue
        cur.execute("""INSERT INTO projects
            (name, client_name, contract_value, material_budget, labor_pct, status, created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (proj_name, pdata.get("client_name",""), pdata.get("contract_value",0), 50000, 40, "Active", datetime.now().isoformat()))
        pid = cur.lastrowid
        for exp in pdata.get("expenses", []):
            cur.execute("""INSERT INTO expenses
                (project_id, expense_date, category, description, amount, is_unplanned, created_at)
                VALUES (?,?,?,?,?,?,?)""",
                (pid, exp.get("Date", datetime.now().date().isoformat()), exp.get("Category","Sundries"), exp.get("Description",""), exp.get("Amount",0), 1 if exp.get("is_unplanned") else 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    log_action("MIGRATION", "system", "json", f"Migrated {JSON_LEGACY} to SQLite, backup {backup}")

def log_action(action, entity, entity_id, details=""):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO audit_log (timestamp, action, entity, entity_id, details) VALUES (?,?,?,?,?)",
                     (datetime.now().isoformat(), action, entity, str(entity_id), details))
        conn.commit()
        conn.close()
    except:
        pass

def q(sql, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

def fetch_one(sql, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    conn.close()
    return row

def fetch_all(sql, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows
