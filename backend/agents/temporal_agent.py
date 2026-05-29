from datetime import datetime, timedelta
from collections import defaultdict

def run_temporal_agent(conn, account_ids, window_hours=2, cluster_mode=False):
    """
    Runs temporal analysis on given account_ids.
    window_hours: time window to check for coordinated activity.
    cluster_mode: if True, runs bank-wide on all dormant activations.
    """
    cursor = conn.cursor()

    if cluster_mode:
        cursor.execute('''
            SELECT txn_id, from_account, to_account, amount, timestamp, channel
            FROM Transactions
            WHERE status = 'COMPLETED'
            ORDER BY timestamp
        ''')
    else:
        placeholders = ",".join("?" for _ in account_ids)
        cursor.execute(f'''
            SELECT txn_id, from_account, to_account, amount, timestamp, channel
            FROM Transactions
            WHERE status = 'COMPLETED'
              AND (from_account IN ({placeholders}) OR to_account IN ({placeholders}))
            ORDER BY timestamp
        ''', (*account_ids, *account_ids))

    rows = cursor.fetchall()

    if not rows:
        return {"agent": "temporal_agent", "findings": [], "log": "No transactions found"}

    txns = []
    for row in rows:
        txn_id, from_acc, to_acc, amount, timestamp, channel = row
        txns.append({
            "txn_id": txn_id,
            "from_account": from_acc,
            "to_account": to_acc,
            "amount": amount,
            "timestamp": timestamp,
            "channel": channel
        })

    findings = []
    log_steps = []

    # 1. Temporal sequence validation — flag reversed sequences
    account_last_seen = {}
    sequence_violations = []
    for t in txns:
        key = (t["from_account"], t["to_account"])
        if key in account_last_seen:
            if t["timestamp"] < account_last_seen[key]:
                sequence_violations.append(t)
        account_last_seen[key] = t["timestamp"]

    if sequence_violations:
        log_steps.append(f"Sequence validation: {len(sequence_violations)} reversed timestamp(s) found")
        findings.append({
            "type": "sequence_violation",
            "detail": f"{len(sequence_violations)} transaction(s) have reversed timestamps — not valid layering chains",
            "accounts": list({t["from_account"] for t in sequence_violations}),
            "score": 0
        })

    # 2. Velocity burst — many transactions in a short window
    account_txn_times = defaultdict(list)
    for t in txns:
        account_txn_times[t["from_account"]].append(t["timestamp"])

    for acc, times in account_txn_times.items():
        if acc not in account_ids and not cluster_mode:
            continue
        times.sort()
        for i in range(len(times)):
            base = datetime.fromisoformat(times[i])
            window_end = (base + timedelta(hours=window_hours)).isoformat()
            burst = [ts for ts in times[i:] if ts <= window_end]
            if len(burst) >= 5:
                log_steps.append(f"Velocity burst: {acc} sent {len(burst)} txns in {window_hours}hr window")
                findings.append({
                    "type": "velocity_burst",
                    "detail": f"Account {acc} sent {len(burst)} transactions within {window_hours} hours",
                    "accounts": [acc],
                    "score": 15
                })
                break

    # 3. Coordinated activation — multiple accounts active in same window
    if cluster_mode:
        # Group all incoming transactions by 2-hour windows
        activation_windows = defaultdict(list)
        for t in txns:
            hour_bucket = t["timestamp"][:13]  # group by hour
            activation_windows[hour_bucket].append(t["to_account"])

        for window, activated_accounts in activation_windows.items():
            unique = list(set(activated_accounts))
            if len(unique) >= 3:
                log_steps.append(f"Coordinated activation at {window}: {len(unique)} accounts")
                findings.append({
                    "type": "coordinated_activation",
                    "detail": f"{len(unique)} accounts activated within the same hour window — coordinated pattern suspected",
                    "accounts": unique,
                    "score": 20
                })

    # 4. Dormancy check on scoped accounts
    if not cluster_mode:
        for acc in account_ids:
            acc_times = sorted(account_txn_times.get(acc, []))
            if len(acc_times) < 2:
                continue
            for i in range(1, len(acc_times)):
                gap = datetime.fromisoformat(acc_times[i]) - datetime.fromisoformat(acc_times[i-1])
                if gap.days >= 90:
                    log_steps.append(f"Dormancy gap: {acc} inactive for {gap.days} days before {acc_times[i]}")
                    findings.append({
                        "type": "dormancy_gap",
                        "detail": f"Account {acc} was inactive for {gap.days} days before reactivating",
                        "accounts": [acc],
                        "score": 10
                    })
                    break

    return {
        "agent": "temporal_agent",
        "findings": findings,
        "log": " | ".join(log_steps) if log_steps else "No temporal anomalies found"
    }