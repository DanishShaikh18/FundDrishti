import sqlite3
from collections import defaultdict
from datetime import datetime

def detect_round_trip(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT txn_id, from_account, to_account, amount, timestamp, channel
        FROM Transactions
        WHERE status = 'COMPLETED'
        ORDER BY timestamp
    ''')
    rows = cursor.fetchall()

    outgoing = defaultdict(list)
    for row in rows:
        txn_id, from_acc, to_acc, amount, timestamp, channel = row
        outgoing[from_acc].append({
            "txn_id": txn_id,
            "from_account": from_acc,
            "to_account": to_acc,
            "amount": amount,
            "timestamp": timestamp,
            "channel": channel
        })

    findings = []
    visited_cycles = set()

    def dfs(start_acc, current_acc, chain, visited):
        if len(chain) > 5:
            return
        for txn in outgoing.get(current_acc, []):
            if chain and txn["timestamp"] <= chain[-1]["timestamp"]:
                continue
            if txn["to_account"] == start_acc and len(chain) >= 2:
                full_chain = chain + [txn]
                start_time = datetime.fromisoformat(full_chain[0]["timestamp"])
                end_time = datetime.fromisoformat(full_chain[-1]["timestamp"])
                hours_elapsed = (end_time - start_time).total_seconds() / 3600
                if hours_elapsed > 72:
                    continue
                sent = full_chain[0]["amount"]
                returned = full_chain[-1]["amount"]
                if abs(sent - returned) / sent > 0.15:
                    continue
                cycle_key = tuple(sorted(t["txn_id"] for t in full_chain))
                if cycle_key in visited_cycles:
                    continue
                visited_cycles.add(cycle_key)
                accounts = list(dict.fromkeys(
                    [t["from_account"] for t in full_chain] +
                    [t["to_account"] for t in full_chain]
                ))
                findings.append({
                    "pattern_type": "round_trip",
                    "confidence": round(min(1.0, 1 - (hours_elapsed / 72) * 0.3), 2),
                    "accounts_involved": accounts,
                    "evidence": {
                        "transactions": full_chain,
                        "finding": (
                            f"Circular transaction detected — ₹{sent:,.0f} left {start_acc} "
                            f"and ₹{returned:,.0f} returned within {hours_elapsed:.1f} hours "
                            f"through {len(chain)} intermediary accounts"
                        )
                    },
                    "score_contribution": 30
                })
                continue
            if txn["to_account"] in visited:
                continue
            dfs(start_acc, txn["to_account"], chain + [txn], visited | {txn["to_account"]})

    for account in outgoing:
        dfs(account, account, [], {account})

    return findings