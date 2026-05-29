from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection
from detectors.structuring import detect_structuring
from detectors.layering import detect_layering
from detectors.round_trip import detect_round_trip
from detectors.dormancy import detect_dormancy
from detectors.profile import detect_profile_mismatch
from agents.orchestrator import investigate
from fusion import compute_final_score
import json

app = FastAPI(title="FundDrishti API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/detect/structuring")
def structuring():
    conn = get_connection()
    results = detect_structuring(conn)
    conn.close()
    return {"pattern": "structuring", "count": len(results), "findings": results}

@app.get("/detect/layering")
def layering():
    conn = get_connection()
    results = detect_layering(conn)
    conn.close()
    return {"pattern": "layering", "count": len(results), "findings": results}

@app.get("/detect/round_trip")
def round_trip():
    conn = get_connection()
    results = detect_round_trip(conn)
    conn.close()
    return {"pattern": "round_trip", "count": len(results), "findings": results}

@app.get("/detect/dormancy")
def dormancy():
    conn = get_connection()
    results = detect_dormancy(conn)
    conn.close()
    return {"pattern": "dormant_activation", "count": len(results), "findings": results}

@app.get("/detect/profile")
def profile():
    conn = get_connection()
    results = detect_profile_mismatch(conn)
    conn.close()
    return {"pattern": "profile_mismatch", "count": len(results), "findings": results}

@app.get("/detect/all")
def detect_all():
    conn = get_connection()
    results = {
        "structuring": detect_structuring(conn),
        "layering": detect_layering(conn),
        "round_trip": detect_round_trip(conn),
        "dormant_activation": detect_dormancy(conn),
        "profile_mismatch": detect_profile_mismatch(conn)
    }
    conn.close()
    total = sum(len(v) for v in results.values())
    return {"total_findings": total, "findings": results}

@app.get("/stats")
def stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Accounts")
    total_accounts = cursor.fetchone()[0]

    cursor.execute("SELECT profile_type, COUNT(*) FROM Accounts GROUP BY profile_type")
    accounts_by_profile = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) FROM Transactions")
    total_transactions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Transactions WHERE status = 'COMPLETED'")
    completed_transactions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Labels WHERE fraud_label = 1")
    fraud_cases = cursor.fetchone()[0]

    cursor.execute("SELECT pattern_type, COUNT(*) FROM Labels WHERE fraud_label = 1 GROUP BY pattern_type")
    fraud_by_pattern = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) FROM Watchlist")
    watchlisted_accounts = cursor.fetchone()[0]

    conn.close()
    return {
        "total_accounts": total_accounts,
        "accounts_by_profile": accounts_by_profile,
        "total_transactions": total_transactions,
        "completed_transactions": completed_transactions,
        "fraud_cases_planted": fraud_cases,
        "fraud_by_pattern": fraud_by_pattern,
        "watchlisted_accounts": watchlisted_accounts
    }

@app.post("/investigate")
def run_investigation(pattern_type: str, accounts: str):
    account_list = [a.strip() for a in accounts.split(",")]
    result = investigate(pattern_type, account_list)
    return result


@app.post("/score")
def score(pattern_type: str, accounts: str):
    account_list = [a.strip() for a in accounts.split(",")]
    conn = get_connection()
    result = compute_final_score(conn, pattern_type, [], account_list)
    conn.close()
    return result


@app.get("/case/{case_id}")
def get_case(case_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"error": "Case not found"}
    return dict(row)

@app.post("/case/{case_id}/sign")
def sign_case(case_id: str, body: dict):
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Cases SET narrative_status = 'SIGNED',
        investigator_name = ?, signed_at = ?
        WHERE case_id = ?
    ''', (body.get("investigator_name"), datetime.now().isoformat(), case_id))
    conn.commit()
    conn.close()
    return {"status": "signed"}

@app.post("/case/{case_id}/generate-fiu")
def generate_fiu(case_id: str):
    from fastapi.responses import FileResponse
    from fiu_package import generate_fiu_package
    conn = get_connection()
    path = generate_fiu_package(conn, case_id)
    conn.close()
    return FileResponse(path, media_type="application/pdf", filename=f"FIU_{case_id}.pdf")