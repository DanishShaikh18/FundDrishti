import sqlite3
import os
import json
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import get_connection, create_tables
from fiu_package import generate_fiu_pdf, generate_fiu_xml

app = FastAPI(title="FundDrishti Backend API", description="AI-Powered AML Investigation API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup downloads directory for serving generated reports
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")

# Standard Pattern Map
PATTERN_MAP = {
    "structuring": "Structuring",
    "layering": "Layering Chain",
    "round_trip": "Round-Trip",
    "dormant_activation": "Coordinated Dormancy",
    "profile_mismatch": "Profile Mismatch"
}

def populate_alerts_and_cases():
    """
    If Alerts and Cases tables are empty, populate them using the Labels data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if Alerts is empty
    cursor.execute("SELECT count(*) FROM Alerts")
    alert_count = cursor.fetchone()[0]
    
    if alert_count > 0:
        conn.close()
        return
        
    print("Populating Alerts and Cases tables from Labels...")
    cursor.execute("SELECT case_id, pattern_type, accounts_involved, fraud_label, difficulty, planted_at FROM Labels")
    labels = cursor.fetchall()
    
    for row in labels:
        case_id, pattern_type, accounts_involved, fraud_label, difficulty, planted_at = row
        accounts_list = accounts_involved.split(',')
        
        # Calculate amount involved from transactions involving these accounts
        placeholders = ','.join('?' for _ in accounts_list)
        cursor.execute(f"""
            SELECT SUM(amount) FROM Transactions 
            WHERE from_account IN ({placeholders}) OR to_account IN ({placeholders})
        """, (*accounts_list, *accounts_list))
        sum_amount = cursor.fetchone()[0]
        if not sum_amount:
            sum_amount = random.uniform(25000.0, 750000.0)
            
        # Determine confidence/risk score
        if fraud_label == 1:
            score = random.randint(76, 98)
        else:
            score = random.randint(35, 62)
            
        display_pattern = PATTERN_MAP.get(pattern_type.lower(), "Structuring")
        status = 'Open'
        created_by = 'System Detector'
        
        # Insert into Alerts
        cursor.execute("""
            INSERT INTO Alerts (alert_id, detected_at, pattern_type, accounts_involved, confidence_score, amount_involved, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (case_id, planted_at, display_pattern, accounts_involved, score, round(sum_amount, 2), status, created_by))
        
        # Breakdown mock
        breakdown = {
            "Velocity Anomaly": random.randint(30, 90),
            "Temporal Match": random.randint(40, 95),
            "Profile Deviation": random.randint(20, 85)
        }
        
        findings = f"Detected potential {display_pattern} involving {len(accounts_list)} accounts. Total volume: ${sum_amount:,.2f}."
        
        narrative = (
            f"ALERT SUMMARY: High-risk {display_pattern} flagged on {planted_at}. "
            f"The network involves the following accounts: {accounts_involved}. "
            f"Analysis reveals coordinated transactions totaling ${sum_amount:,.2f}. "
            f"Account behavior deviates significantly from established peer group baselines, showing "
            f"an anomaly in frequency and geographic endpoints. Immediate investigator action is recommended."
        )
        
        # Insert into Cases
        cursor.execute("""
            INSERT INTO Cases (case_id, alert_id, risk_score, score_breakdown, agent_findings, narrative_draft, narrative_status, investigator_name, signed_at, fiu_generated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (case_id, case_id, score, json.dumps(breakdown), findings, narrative, 'DRAFT', None, None, 0))
        
    conn.commit()
    conn.close()
    print("Populating completed.")

@app.on_event("startup")
def startup_event():
    create_tables()
    populate_alerts_and_cases()

class StatusUpdate(BaseModel):
    status: str
    investigator_notes: str = ""

class FiuGeneration(BaseModel):
    investigator_name: str
    verified: bool

@app.get("/")
def read_root():
    return {"message": "Welcome to FundDrishti Investigation API", "status": "running"}

@app.get("/alerts")
def get_alerts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT alert_id, pattern_type, confidence_score, accounts_involved, amount_involved, detected_at, status 
        FROM Alerts 
        ORDER BY confidence_score DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    alerts_list = []
    for r in rows:
        num_accounts = len(r['accounts_involved'].split(',')) if r['accounts_involved'] else 0
        alerts_list.append({
            "id": r['alert_id'],
            "pattern_type": r['pattern_type'],
            "score": int(r['confidence_score']),
            "accounts": num_accounts,
            "amount": float(r['amount_involved']),
            "timestamp": r['detected_at'],
            "status": r['status']
        })
    return alerts_list

@app.get("/cases/{case_id}")
def get_case(case_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch Case Metadata
    cursor.execute("""
        SELECT c.case_id, c.risk_score, c.score_breakdown, c.agent_findings, c.narrative_draft, c.narrative_status, c.investigator_name, c.signed_at, c.fiu_generated,
               a.pattern_type, a.accounts_involved, a.detected_at, a.status, a.amount_involved
        FROM Cases c
        JOIN Alerts a ON c.alert_id = a.alert_id
        WHERE c.case_id = ?
    """, (case_id,))
    
    case_row = cursor.fetchone()
    if not case_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")
        
    accounts_involved_str = case_row['accounts_involved']
    accounts_list = accounts_involved_str.split(',') if accounts_involved_str else []
    
    # Fetch Accounts Info
    accounts_info = []
    placeholders = ','.join('?' for _ in accounts_list)
    
    if accounts_list:
        cursor.execute(f"""
            SELECT account_id, customer_name, profile_type, declared_annual_income 
            FROM Accounts 
            WHERE account_id IN ({placeholders})
        """, accounts_list)
        acc_rows = {r['account_id']: r for r in cursor.fetchall()}
    else:
        acc_rows = {}
        
    for i, acc_id in enumerate(accounts_list):
        acc_db = acc_rows.get(acc_id)
        name = acc_db['customer_name'] if acc_db else "Unknown Account"
        profile = acc_db['profile_type'] if acc_db else "Student"
        
        # Count transactions for this account
        cursor.execute("SELECT count(*) FROM Transactions WHERE from_account = ? OR to_account = ?", (acc_id, acc_id))
        tx_count = cursor.fetchone()[0]
        
        # Determine roles: First is suspect, others are intermediaries/victims
        if i == 0:
            role = "Suspect"
        elif i == 1:
            role = "Victim"
        else:
            role = "Intermediary"
            
        accounts_info.append({
            "id": acc_id,
            "name": name,
            "role": role,
            "transactions_count": tx_count,
            "profile_type": profile
        })
        
    # Build Network Subgraph (nodes and edges)
    nodes = []
    edges = []
    
    for acc in accounts_info:
        nodes.append({
            "id": acc["id"],
            "label": acc["name"],
            "role": acc["role"].lower()
        })
        
    if accounts_list:
        cursor.execute(f"""
            SELECT txn_id, from_account, to_account, amount, timestamp, channel, narration 
            FROM Transactions 
            WHERE from_account IN ({placeholders}) AND to_account IN ({placeholders})
        """, (*accounts_list, *accounts_list))
        txs = cursor.fetchall()
        for t in txs:
            edges.append({
                "source": t['from_account'],
                "target": t['to_account'],
                "amount": float(t['amount']),
                "timestamp": t['timestamp'],
                "channel": t['channel'],
                "narration": t['narration']
            })
            
    # Mock behavioral profiles normalized to 0-100 scale for Radar Chart
    behavioral_profile = {
        "victim": {
            "account_age_days": 75,
            "avg_transaction_size": 40,
            "transaction_frequency": 25,
            "dormancy_days": 10,
            "geographic_variance": 15,
            "network_centrality": 20,
            "risk_indicator": 15
        },
        "suspect": {
            "account_age_days": 20,
            "avg_transaction_size": 85,
            "transaction_frequency": 90,
            "dormancy_days": 65,
            "geographic_variance": 80,
            "network_centrality": 75,
            "risk_indicator": int(case_row['risk_score'])
        },
        "baseline": {
            "account_age_days": 60,
            "avg_transaction_size": 45,
            "transaction_frequency": 35,
            "dormancy_days": 15,
            "geographic_variance": 20,
            "network_centrality": 30,
            "risk_indicator": 30
        }
    }
    
    # Format dates
    created_at = case_row['detected_at']
    updated_at = case_row['detected_at'] # Fallback if no update date exists
    
    res = {
        "id": case_row['case_id'],
        "pattern_type": case_row['pattern_type'],
        "score": int(case_row['risk_score']),
        "summary": case_row['agent_findings'], # Short overview summary
        "narrative_draft": case_row['narrative_draft'], # Detailed AI narrative
        "accounts": accounts_info,
        "transaction_subgraph": {
            "nodes": nodes,
            "edges": edges
        },
        "behavioral_profile": behavioral_profile,
        "status": case_row['status'],
        "created_at": created_at,
        "updated_at": updated_at,
        "investigator_name": case_row['investigator_name'],
        "signed_at": case_row['signed_at'],
        "fiu_generated": int(case_row['fiu_generated'])
    }
    
    conn.close()
    return res

@app.put("/cases/{case_id}/status")
def update_case_status(case_id: str, payload: StatusUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if case exists
    cursor.execute("SELECT count(*) FROM Cases WHERE case_id = ?", (case_id,))
    exists = cursor.fetchone()[0]
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Update Status in Alerts
    cursor.execute("UPDATE Alerts SET status = ? WHERE alert_id = ?", (payload.status, case_id))
    
    # Update Case notes if provided
    if payload.investigator_notes:
        cursor.execute("UPDATE Cases SET agent_findings = ? WHERE case_id = ?", (payload.investigator_notes, case_id))
        
    conn.commit()
    conn.close()
    return {"id": case_id, "status": payload.status, "updated_at": datetime.utcnow().isoformat() + "Z"}

@app.post("/alert/{case_id}/generate-fiu")
@app.post("/cases/{case_id}/generate-fiu")
def generate_fiu(case_id: str, payload: FiuGeneration):
    if not payload.verified:
        raise HTTPException(status_code=400, detail="Case must be verified by the investigator first.")
        
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT count(*) FROM Cases WHERE case_id = ?", (case_id,))
    exists = cursor.fetchone()[0]
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")
        
    signed_time = datetime.utcnow().isoformat() + "Z"
    
    # Update Case table
    cursor.execute("""
        UPDATE Cases 
        SET investigator_name = ?, signed_at = ?, fiu_generated = 1 
        WHERE case_id = ?
    """, (payload.investigator_name, signed_time, case_id))
    
    # Also update Alert status to Closed
    cursor.execute("UPDATE Alerts SET status = 'Closed' WHERE alert_id = ?", (case_id,))
    conn.commit()
    conn.close()
    
    # Generate the actual case details payload to feed generators
    case_details = get_case(case_id)
    
    # Output file paths
    pdf_filename = f"{case_id}_FIU_Report.pdf"
    xml_filename = f"{case_id}_goAML_Package.xml"
    
    pdf_path = os.path.join(DOWNLOADS_DIR, pdf_filename)
    xml_path = os.path.join(DOWNLOADS_DIR, xml_filename)
    
    # Run ReportLab and xml tree generators
    try:
        generate_fiu_pdf(case_id, case_details, pdf_path)
        generate_fiu_xml(case_id, case_details, xml_path)
    except Exception as e:
        print("Error generating report files:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate files: {str(e)}")
        
    return {
        "success": True,
        "message": "FIU Evidence Package generated successfully.",
        "case_id": case_id,
        "investigator": payload.investigator_name,
        "signed_at": signed_time,
        "download_pdf": f"/downloads/{pdf_filename}",
        "download_xml": f"/downloads/{xml_filename}"
    }
