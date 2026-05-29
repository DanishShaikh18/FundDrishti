import sqlite3
import os

# Resolve the absolute path to the database to ensure it always points to the correct location 
# regardless of where the script is run from (backend/ or root directory).
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'funddrishti.db')

def get_connection():
    """
    Opens and returns a connection to data/funddrishti.db.
    Every other file in the project should import this when it needs the database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def create_tables():
    """
    Runs all six CREATE TABLE statements in one shot. 
    You call this once when setting up. 
    After that it does nothing because of IF NOT EXISTS.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Accounts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Accounts (
            account_id TEXT PRIMARY KEY,
            customer_name TEXT,
            account_type TEXT,
            profile_type TEXT,
            declared_annual_income REAL,
            branch_code TEXT,
            account_opened_date TEXT,
            is_watchlisted INTEGER DEFAULT 0,
            pan_number TEXT,
            mobile_number TEXT
        )
    ''')
    
    # 2. Transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            txn_id TEXT PRIMARY KEY,
            txn_reference TEXT,
            timestamp TEXT,
            from_account TEXT,
            to_account TEXT,
            amount REAL,
            channel TEXT,
            status TEXT DEFAULT 'COMPLETED',
            narration TEXT
        )
    ''')
    
    # 3. Labels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Labels (
            case_id TEXT PRIMARY KEY,
            pattern_type TEXT,
            accounts_involved TEXT,
            fraud_label INTEGER,
            difficulty TEXT,
            planted_at TEXT
        )
    ''')
    
    # 4. Watchlist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Watchlist (
            account_id TEXT PRIMARY KEY,
            reason_flagged TEXT,
            flagged_date TEXT,
            flag_source TEXT
        )
    ''')
    
    # 5. Alerts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Alerts (
            alert_id TEXT PRIMARY KEY,
            detected_at TEXT,
            pattern_type TEXT,
            accounts_involved TEXT,
            confidence_score REAL,
            amount_involved REAL,
            status TEXT DEFAULT 'NEW',
            created_by TEXT
        )
    ''')
    
    # 6. Cases
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Cases (
            case_id TEXT PRIMARY KEY,
            alert_id TEXT,
            pattern_type TEXT,
            risk_score REAL,
            score_breakdown TEXT,
            agent_findings TEXT,
            narrative_draft TEXT,
            narrative_status TEXT DEFAULT 'DRAFT',
            investigator_name TEXT,
            signed_at TEXT,
            fiu_generated INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database tables verified/created successfully.")
