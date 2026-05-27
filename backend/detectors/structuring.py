import sqlite3
from collections import defaultdict

def detect_structuring(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT txn_id, from_account, to_account, amount, timestamp, channel
        FROM Transactions
        WHERE status = 'COMPLETED'
          AND channel IN ('RTGS', 'NEFT')
          AND amount BETWEEN 800000 AND 999000
        ORDER BY timestamp
    ''')
    rows = cursor.fetchall()

    # Group by (to_account, date)
    groups = defaultdict(list)
    for row in rows:
        txn_id, from_acc, to_acc, amount, timestamp, channel = row
        date = timestamp[:10]
        groups[(to_acc, date)].append({
            "txn_id": txn_id,
            "from_account": from_acc,
            "to_account": to_acc,
            "amount": amount,
            "timestamp": timestamp,
            "channel": channel
        })

    findings = []
    for (to_acc, date), txns in groups.items():
        # Deduplicate by from_account
        seen = {}
        for t in txns:
            seen[t["from_account"]] = t
        unique_sources = list(seen.values())

        if len(unique_sources) < 3:
            continue

        count = len(unique_sources)
        all_accounts = list({t["from_account"] for t in unique_sources} | {to_acc})

        findings.append({
            "pattern_type": "structuring",
            "confidence": round(min(count / 5, 1.0), 2),
            "accounts_involved": all_accounts,
            "evidence": {
                "transactions": unique_sources,
                "finding": (
                    f"{count} accounts sent amounts between ₹8L-₹9.99L to {to_acc} "
                    f"on {date} — potential structuring below CTR threshold"
                )
            },
            "score_contribution": 35
        })

    return findings