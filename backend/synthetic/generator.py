import sqlite3
import random
import os
import sys
from datetime import datetime, timedelta

try:
    from faker import Faker
except ImportError:
    print("Faker not found. Please run: pip install faker")
    sys.exit(1)

# Import get_connection from backend/database.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

random.seed(42)
fake = Faker('en_IN')
Faker.seed(42)

def generate_accounts(conn):
    cursor = conn.cursor()
    profiles = ['Student'] * 125 + ['Salaried'] * 125 + ['SmallBusiness'] * 125 + ['CashBusiness'] * 125
    random.shuffle(profiles)
    
    accounts = []
    watchlisted_ids = [f"ACC_WATCH_{i}" for i in range(1, 11)]
    
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    for i, profile in enumerate(profiles):
        if i < 10:
            acc_id = watchlisted_ids[i]
            is_watchlisted = 1
        else:
            acc_id = f"ACC_{fake.unique.random_number(digits=8, fix_len=True)}"
            is_watchlisted = 0
            
        accounts.append(acc_id)
        customer_name = fake.name()
        
        if profile == 'Student':
            account_type = 'SAVINGS'
            income = random.uniform(0, 200000)
        elif profile == 'Salaried':
            account_type = 'SAVINGS'
            income = random.uniform(300000, 2500000)
        elif profile == 'SmallBusiness':
            account_type = 'CURRENT'
            income = random.uniform(1000000, 10000000)
        else: # CashBusiness
            account_type = 'CURRENT'
            income = random.uniform(500000, 5000000)
            
        branch_code = f"BR_{fake.random_number(digits=4, fix_len=True)}"
        opened_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        
        pan_number = "ABCPXXXXX1234"
        mobile_number = f"9{fake.random_number(digits=9, fix_len=True)}"
        
        cursor.execute('''
            INSERT INTO Accounts (account_id, customer_name, account_type, profile_type, declared_annual_income, branch_code, account_opened_date, is_watchlisted, pan_number, mobile_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (acc_id, customer_name, account_type, profile, income, branch_code, opened_date.isoformat(), is_watchlisted, pan_number, mobile_number))
        
        if is_watchlisted == 1:
            flagged_date = (opened_date + timedelta(days=random.randint(1, 100))).isoformat()
            cursor.execute('''
                INSERT INTO Watchlist (account_id, reason_flagged, flagged_date, flag_source)
                VALUES (?, ?, ?, ?)
            ''', (acc_id, 'Suspicious Activity', flagged_date, 'RBI'))
            
    conn.commit()
    return accounts

def generate_transactions(conn, accounts):
    cursor = conn.cursor()
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for i in range(5000):
        txn_id = f"TXN_BASE_{i}"
        from_acc, to_acc = random.sample(accounts, 2)
        
        channels = ['UPI', 'RTGS', 'IMPS', 'CASH', 'NEFT']
        channel = random.choice(channels)
        
        if channel == 'UPI':
            amount = random.uniform(10, 100000)
            txn_ref = f"UPI{fake.random_number(digits=12, fix_len=True)}"
        elif channel == 'RTGS':
            amount = random.uniform(200000, 10000000)
            txn_ref = f"UNIONB24{fake.random_number(digits=14, fix_len=True)}"
        elif channel == 'IMPS':
            amount = random.uniform(10, 500000)
            txn_ref = f"IMPS{fake.random_number(digits=10, fix_len=True)}"
        elif channel == 'CASH':
            amount = random.uniform(100, 50000)
            txn_ref = f"CASH{fake.random_number(digits=8, fix_len=True)}"
        else: # NEFT
            amount = random.uniform(10, 5000000)
            txn_ref = f"UNIONB24{fake.random_number(digits=14, fix_len=True)}"
            
        timestamp = start_date + timedelta(days=random.randint(0, (end_date - start_date).days), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        cursor.execute('''
            INSERT INTO Transactions (txn_id, txn_reference, timestamp, from_account, to_account, amount, channel, status, narration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (txn_id, txn_ref, timestamp.isoformat(), from_acc, to_acc, round(amount, 2), channel, 'COMPLETED', fake.sentence(nb_words=3)))
        
    conn.commit()

def verify(conn):
    cursor = conn.cursor()
    print("\n--- Verification Report ---")
    
    cursor.execute("SELECT profile_type, count(*) FROM Accounts GROUP BY profile_type")
    print("Accounts per profile type:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
        
    cursor.execute("SELECT count(*) FROM Transactions")
    print(f"\nTotal Transactions: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT pattern_type, count(*) FROM Labels WHERE fraud_label = 1 GROUP BY pattern_type")
    print("\nFraud Cases per pattern type:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
        
    cursor.execute("SELECT count(*) FROM Labels WHERE fraud_label = 0")
    print(f"\nClean-but-suspicious Cases: {cursor.fetchone()[0]}")
        
    cursor.execute("SELECT case_id, accounts_involved FROM Labels WHERE pattern_type = 'structuring' LIMIT 1")
    sample_case = cursor.fetchone()
    if sample_case:
        case_id = sample_case[0]
        accs = sample_case[1].split(',')
        print(f"\nSample Structuring Case: {case_id}")
        print(f"Accounts Involved: {accs}")
        
        placeholders = ','.join('?' for _ in accs)
        cursor.execute(f"SELECT txn_id, timestamp, from_account, to_account, amount, channel FROM Transactions WHERE from_account IN ({placeholders}) OR to_account IN ({placeholders}) ORDER BY timestamp", (*accs, *accs))
        print("Transactions:")
        for t in cursor.fetchall():
            print(f"  {t[0]} | {t[1]} | {t[2]} -> {t[3]} | {t[4]:.2f} | {t[5]}")

if __name__ == "__main__":
    conn = get_connection()
    
    # Clean up before generation
    conn.execute("DELETE FROM Accounts")
    conn.execute("DELETE FROM Transactions")
    conn.execute("DELETE FROM Labels")
    conn.execute("DELETE FROM Watchlist")
    conn.commit()
    
    print("Generating Accounts...")
    accs = generate_accounts(conn)
    print("Generating Baseline Transactions...")
    generate_transactions(conn, accs)
    
    print("Planting Fraud Cases...")
    import fraud_planters
    for _ in range(40):
        fraud_planters.plant_structuring(conn, accs)
        fraud_planters.plant_layering(conn, accs)
        fraud_planters.plant_round_trip(conn, accs)
        fraud_planters.plant_dormant_activation(conn, accs)
        fraud_planters.plant_profile_mismatch(conn, accs)
        
    for _ in range(50):
        fraud_planters.plant_clean_suspicious(conn, accs)
    
    verify(conn)
    conn.close()
