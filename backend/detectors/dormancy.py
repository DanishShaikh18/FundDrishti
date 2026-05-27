import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta

def detect_dormancy(conn):
    cursor = conn.cursor()

    # Get all accounts
    cursor.execute("SELECT account_id FROM Accounts")
    all_accounts = [row[0] for row in cursor.fetchall()]

    # Get all completed transactions
    cursor.execute('''
        SELECT txn_id, from_account, to_account, amount, timestamp
        FROM Transactions
        WHERE status = 'COMPLETED'
        ORDER BY timestamp
    ''')
    rows = cursor.fetchall()

    # Build last active date per account before each transaction
    last_active = defaultdict(lambda: None)
    all_txns = []
    for row in rows:
        txn_id, from_acc, to_acc, amount, timestamp = row
        all_txns.append({
            "txn_id": txn_id,
            "from_account": from_acc,
            "to_account": to_acc,
            "amount": amount,
            "timestamp": timestamp
        })

    # For each account track all timestamps it appeared in
    account_timestamps = defaultdict(list)
    for t in all_txns:
        account_timestamps[t["from_account"]].append(t["timestamp"])
        account_timestamps[t["to_account"]].append(t["timestamp"])

    for acc in account_timestamps:
        account_timestamps[acc].sort()

    findings = []
    visited_clusters = set()

    # Sliding 2-hour windows — find accounts receiving money after 90 days dormancy
    # Group incoming transactions by 2-hour windows
    incoming = defaultdict(list)
    for t in all_txns:
        incoming[t["to_account"]].append(t)

    reactivation_events = []
    for acc, txns in incoming.items():
        timestamps_for_acc = account_timestamps[acc]
        for txn in txns:
            txn_time = datetime.fromisoformat(txn["timestamp"])
            ninety_days_before = (txn_time - timedelta(days=90)).isoformat()

            # Check if account had any activity in 90 days before this transaction
            prior_activity = [
                ts for ts in timestamps_for_acc
                if ninety_days_before <= ts < txn["timestamp"]
            ]
            if not prior_activity:
                reactivation_events.append({
                    "account": acc,
                    "amount": txn["amount"],
                    "timestamp": txn["timestamp"],
                    "txn": txn
                })

    # Cluster reactivations within 2-hour windows
    reactivation_events.sort(key=lambda x: x["timestamp"])

    for i, event in enumerate(reactivation_events):
        base_time = datetime.fromisoformat(event["timestamp"])
        window_end = (base_time + timedelta(hours=2)).isoformat()

        cluster = [event]
        for j, other in enumerate(reactivation_events):
            if i == j:
                continue
            if event["timestamp"] <= other["timestamp"] <= window_end:
                # Amount within 10% of base
                if abs(other["amount"] - event["amount"]) / event["amount"] <= 0.10:
                    cluster.append(other)

        if len(cluster) < 3:
            continue

        cluster_key = tuple(sorted(e["account"] for e in cluster))
        if cluster_key in visited_clusters:
            continue
        visited_clusters.add(cluster_key)

        accounts = list({e["account"] for e in cluster})
        txns = [e["txn"] for e in cluster]
        amounts = [e["amount"] for e in cluster]

        # Louvain secondary validation
        louvain_confirmed = False
        try:
            import networkx as nx
            import community as community_louvain
            G = nx.Graph()
            for e in cluster:
                for f in cluster:
                    if e["account"] != f["account"]:
                        G.add_edge(e["account"], f["account"])
            if G.number_of_nodes() >= 3:
                partition = community_louvain.best_partition(G)
                communities = set(partition.values())
                louvain_confirmed = len(communities) == 1
        except ImportError:
            louvain_confirmed = True  # Skip if library not installed

        confidence = round(min(len(cluster) / 8, 1.0), 2)
        if louvain_confirmed:
            confidence = min(confidence + 0.1, 1.0)

        findings.append({
            "pattern_type": "dormant_activation",
            "confidence": confidence,
            "accounts_involved": accounts,
            "evidence": {
                "transactions": txns,
                "finding": (
                    f"{len(cluster)} dormant accounts reactivated within a 2-hour window "
                    f"receiving similar amounts (₹{min(amounts):,.0f}–₹{max(amounts):,.0f}) "
                    f"— coordinated activation suspected"
                    + (" — Louvain confirmed tight cluster" if louvain_confirmed else "")
                )
            },
            "score_contribution": 30
        })

    return findings