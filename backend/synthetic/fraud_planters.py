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
        amount = random.uniform(800000, 999000) # Below 10L CTR threshold
        channel = random.choice(['RTGS', 'NEFT'])
        ref = f"UNIONB24{random.randint(10000000000000, 99999999999999)}"
        txns.append((txn_id, ref, (base_time + timedelta(hours=i)).isoformat(), smurf, target_acc, round(amount, 2), channel, 'COMPLETED', 'Investment Transfer'))
        
    _plant_txns_and_label(conn, txns, 'structuring', [target_acc] + smurfs, 1, 'standard')


def plant_layering(conn, accounts):
    chain = random.sample(accounts, 4)
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    amount = random.uniform(400000, 490000) # Capped at 4.9L for IMPS limit
    
    for i in range(len(chain)-1):
        txn_id = f"TXN_LAY_{uuid.uuid4().hex[:6]}"
        ref = f"IMPS{random.randint(10000000, 99999999)}"
        txns.append((txn_id, ref, (base_time + timedelta(minutes=i*10)).isoformat(), chain[i], chain[i+1], round(amount, 2), 'IMPS', 'COMPLETED', 'Transfer'))
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
        ref = f"UNIONB24{random.randint(10000000000000, 99999999999999)}" # Correct RTGS format
        txns.append((txn_id, ref, (base_time + timedelta(days=i)).isoformat(), cycle[i], cycle[i+1], round(amount, 2), 'RTGS', 'COMPLETED', 'Business Payment'))
        
    _plant_txns_and_label(conn, txns, 'round_trip', cycle[:-1], 1, 'standard')


def plant_dormant_activation(conn, accounts):
    num_dormant = random.randint(3, 8)
    dormants = random.sample(accounts, num_dormant)
    
    txns = []
    base_time = datetime(2024, random.randint(4, 12), random.randint(1, 28)) # Ensure >90 days into year
    ninety_days_ago = (base_time - timedelta(days=90)).isoformat()
    
    # Delete transactions for these accounts in the 90 days prior to base_time to simulate dormancy
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in dormants)
    cursor.execute(f"DELETE FROM Transactions WHERE (from_account IN ({placeholders}) OR to_account IN ({placeholders})) AND timestamp BETWEEN ? AND ?", (*dormants, *dormants, ninety_days_ago, base_time.isoformat()))
    
    base_amount = random.uniform(500000, 2000000)
    
    for i, dormant_acc in enumerate(dormants):
        peer = random.choice([a for a in accounts if a not in dormants])
        amount = base_amount + random.uniform(-10000, 10000)
        txn_id = f"TXN_DRM_{uuid.uuid4().hex[:6]}"
        channel = 'NEFT'
        ref = f"UNIONB24{random.randint(10000000000000, 99999999999999)}"
        timestamp = (base_time + timedelta(minutes=random.randint(0, 120))).isoformat() # all activating within 2 hours
        
        txns.append((txn_id, ref, timestamp, peer, dormant_acc, round(amount, 2), channel, 'COMPLETED', 'Account Reactivation Transfer'))
        
    _plant_txns_and_label(conn, txns, 'dormant_activation', dormants, 1, 'standard')


def plant_profile_mismatch(conn, accounts):
    acc = random.choice(accounts)
    counterparties = random.sample([a for a in accounts if a != acc], 10)
    
    txns = []
    base_time = datetime(2024, random.randint(1, 12), random.randint(1, 28))
    
    for i in range(15):
        peer = random.choice(counterparties)
        amount = random.uniform(500000, 2000000) 
        txn_id = f"TXN_PRF_{uuid.uuid4().hex[:6]}"
        channel = random.choice(['RTGS', 'NEFT'])
        ref = f"UNIONB24{random.randint(10000000000000, 99999999999999)}"
        timestamp = (base_time + timedelta(hours=random.uniform(0, 24))).isoformat()
        
        if random.random() > 0.5:
            from_acc, to_acc = peer, acc
        else:
            from_acc, to_acc = acc, peer
            
        txns.append((txn_id, ref, timestamp, from_acc, to_acc, round(amount, 2), channel, 'COMPLETED', 'Investment/Trading'))
    
    _plant_txns_and_label(conn, txns, 'profile_mismatch', [acc] + counterparties, 1, 'standard')


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
        txns.append((f"TXN_CLN_{uuid.uuid4().hex[:6]}", f"UNIONB24{random.randint(10000000000000, 99999999999999)}", base_time.isoformat(), buyer, farmer, round(amount, 2), 'RTGS', 'COMPLETED', 'Crop Sale'))
        _plant_txns_and_label(conn, txns, pattern, [farmer, buyer], 0, 'clean_suspicious')
