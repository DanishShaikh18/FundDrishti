import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'funddrishti.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Get row counts
for table in tables:
    cursor.execute(f"SELECT count(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Table '{table}': {count} rows")

# Print a few samples of Alerts and Cases if they exist
for table in ['Alerts', 'Cases', 'Labels']:
    if table in tables:
        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
        rows = cursor.fetchall()
        print(f"\nSample rows from {table}:")
        for r in rows:
            print(" ", r)

conn.close()
