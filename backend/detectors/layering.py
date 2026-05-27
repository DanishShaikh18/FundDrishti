import sqlite3
from collections import defaultdict

def detect_layering(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT txn_id, from_account, to_account, amount, timestamp, channel
        FROM Transactions
        WHERE status = 'COMPLETED'
        ORDER BY timestamp
    ''')
    rows = cursor.fetchall()

    # Build adjacency: from_account -> list of outgoing transactions
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
    visited_chains = set()

    def bfs(start_acc):
        # Each queue item: (current_account, chain_so_far)
        queue = [(start_acc, [])]
        while queue:
            current, chain = queue.pop(0)
            for txn in outgoing.get(current, []):
                # Temporal validation: timestamp must be after last hop
                if chain and txn["timestamp"] <= chain[-1]["timestamp"]:
                    continue
                # Amount must not drop more than 20% from previous hop
                if chain and txn["amount"] < chain[-1]["amount"] * 0.80:
                    continue
                new_chain = chain + [txn]
                if len(new_chain) >= 3:
                    chain_key = tuple(t["txn_id"] for t in new_chain)
                    if chain_key not in visited_chains:
                        visited_chains.add(chain_key)
                        accounts = [new_chain[0]["from_account"]] + [t["to_account"] for t in new_chain]
                        findings.append({
                            "pattern_type": "layering",
                            "confidence": round(min(len(new_chain) / 5, 1.0), 2),
                            "accounts_involved": list(dict.fromkeys(accounts)),
                            "evidence": {
                                "transactions": new_chain,
                                "finding": (
                                    f"{len(new_chain)}-hop layering chain detected from "
                                    f"{new_chain[0]['from_account']} — funds moved rapidly "
                                    f"with strict timestamp progression and minimal skimming"
                                )
                            },
                            "score_contribution": 25
                        })
                # Continue BFS only up to 5 hops
                if len(new_chain) < 5:
                    queue.append((txn["to_account"], new_chain))

    for account in outgoing:
        bfs(account)

    return findings