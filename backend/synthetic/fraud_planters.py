import random
import uuid
import sys
import os
from datetime import datetime, timedelta

# Add backend to sys.path to import get_connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

def _plant_txns_and_label(conn, txns, pattern_type, accounts_involved, fraud_label, difficulty):
    cursor = conn.cursor()
    case_id = f"CASE_{uuid.uuid4().hex[:8].upper()}"
    planted_at = datetime.now().isoformat()
    
    for t in txns:
        cursor.execute('''
            INSERT INTO Transactions (txn_id, txn_reference, timestamp, from_account, to_account, amount, channel, status, narration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', t)
        
    cursor.execute('''
        INSERT INTO Labels (case_id, pattern_type, accounts_involved, fraud_label, difficulty, planted_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (case_id, pattern_type, ",".join(accounts_involved), fraud_label, difficulty, planted_at))
    conn.commit()

def plant_structuring(conn, accounts):
    target_acc = random.choice(accounts)
    smurfs = random.sample([a for a in accounts if a != target_acc], 5)
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    
    for i, smurf in enumerate(smurfs):
        txn_id = f"TXN_STR_{uuid.uuid4().hex[:6]}"
        amount = random.uniform(45000, 49999) # Below 50k CASH threshold
        txns.append((txn_id, f"CASH{random.randint(10000000, 99999999)}", (base_time + timedelta(hours=i)).isoformat(), smurf, target_acc, round(amount, 2), 'CASH', 'COMPLETED', 'Deposit'))
        
    _plant_txns_and_label(conn, txns, 'structuring', [target_acc] + smurfs, 1, 'standard')

def plant_layering(conn, accounts):
    chain = random.sample(accounts, 4)
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    amount = random.uniform(500000, 1000000)
    
    for i in range(len(chain)-1):
        txn_id = f"TXN_LAY_{uuid.uuid4().hex[:6]}"
        txns.append((txn_id, f"IMPS{random.randint(10000000, 99999999)}", (base_time + timedelta(minutes=i*10)).isoformat(), chain[i], chain[i+1], round(amount, 2), 'IMPS', 'COMPLETED', 'Transfer'))
        amount -= random.uniform(1000, 5000)
        
    _plant_txns_and_label(conn, txns, 'layering', chain, 1, 'standard')

def plant_round_trip(conn, accounts):
    cycle = random.sample(accounts, 3)
    cycle.append(cycle[0])
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    amount = random.uniform(200000, 500000)
    
    for i in range(len(cycle)-1):
        txn_id = f"TXN_RND_{uuid.uuid4().hex[:6]}"
        txns.append((txn_id, f"RTGS{random.randint(10000000, 99999999)}", (base_time + timedelta(days=i)).isoformat(), cycle[i], cycle[i+1], round(amount, 2), 'RTGS', 'COMPLETED', 'Business Payment'))
        
    _plant_txns_and_label(conn, txns, 'round_trip', cycle[:-1], 1, 'standard')

def plant_dormant_activation(conn, accounts):
    acc = random.choice(accounts)
    peer = random.choice([a for a in accounts if a != acc])
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    amount = random.uniform(1000000, 5000000)
    
    txns.append((f"TXN_DRM_{uuid.uuid4().hex[:6]}", f"NEFT{random.randint(10000000, 99999999)}", base_time.isoformat(), peer, acc, round(amount, 2), 'NEFT', 'COMPLETED', 'Fund Transfer'))
    txns.append((f"TXN_DRM_{uuid.uuid4().hex[:6]}", f"RTGS{random.randint(10000000, 99999999)}", (base_time + timedelta(days=1)).isoformat(), acc, peer, round(amount-1000, 2), 'RTGS', 'COMPLETED', 'Return'))
    
    _plant_txns_and_label(conn, txns, 'dormant_activation', [acc, peer], 1, 'standard')

def plant_profile_mismatch(conn, accounts):
    acc = random.choice(accounts)
    peer = random.choice([a for a in accounts if a != acc])
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    amount = random.uniform(5000000, 10000000) 
    
    txns.append((f"TXN_PRF_{uuid.uuid4().hex[:6]}", f"RTGS{random.randint(10000000, 99999999)}", base_time.isoformat(), peer, acc, round(amount, 2), 'RTGS', 'COMPLETED', 'Investment'))
    
    _plant_txns_and_label(conn, txns, 'profile_mismatch', [acc, peer], 1, 'standard')

def plant_clean_suspicious(conn, accounts):
    patterns = ['nri_remittance', 'bulk_payroll', 'seasonal_agricultural']
    pattern = random.choice(patterns)
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    
    if pattern == 'nri_remittance':
        acc = random.choice(accounts)
        amount = random.uniform(100000, 500000)
        txns.append((f"TXN_CLN_{uuid.uuid4().hex[:6]}", f"NEFT{random.randint(10000000, 99999999)}", base_time.isoformat(), "EXT_NRI_ACC", acc, round(amount, 2), 'NEFT', 'COMPLETED', 'Family Maintenance'))
        _plant_txns_and_label(conn, txns, pattern, [acc], 0, 'clean_suspicious')
        
    elif pattern == 'bulk_payroll':
        company = random.choice(accounts)
        employees = random.sample([a for a in accounts if a != company], 5)
        for i, emp in enumerate(employees):
            amount = random.uniform(20000, 80000)
            txns.append((f"TXN_CLN_{uuid.uuid4().hex[:6]}", f"NEFT{random.randint(10000000, 99999999)}", (base_time + timedelta(minutes=i)).isoformat(), company, emp, round(amount, 2), 'NEFT', 'COMPLETED', 'Salary'))
        _plant_txns_and_label(conn, txns, pattern, [company] + employees, 0, 'clean_suspicious')
        
    elif pattern == 'seasonal_agricultural':
        farmer = random.choice(accounts)
        buyer = random.choice([a for a in accounts if a != farmer])
        amount = random.uniform(300000, 800000)
        txns.append((f"TXN_CLN_{uuid.uuid4().hex[:6]}", f"RTGS{random.randint(10000000, 99999999)}", base_time.isoformat(), buyer, farmer, round(amount, 2), 'RTGS', 'COMPLETED', 'Crop Sale'))
        _plant_txns_and_label(conn, txns, pattern, [farmer, buyer], 0, 'clean_suspicious')

if __name__ == "__main__":
    random.seed(42)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_id FROM Accounts")
    accs = [r[0] for r in cursor.fetchall()]
    
    if not accs:
        print("No accounts found. Please run generator.py first.")
        sys.exit(1)
        
    for _ in range(40):
        plant_structuring(conn, accs)
        plant_layering(conn, accs)
        plant_round_trip(conn, accs)
        plant_dormant_activation(conn, accs)
        plant_profile_mismatch(conn, accs)
        
    for _ in range(50):
        plant_clean_suspicious(conn, accs)
        
    print("Planted 200 fraud cases and 50 clean-but-suspicious cases successfully.")
    conn.close()
