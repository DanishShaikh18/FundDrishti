from detectors.profile import detect_profile_mismatch, _compute_features, BENCHMARKS, _zscore

def run_profile_agent(conn, account_ids):
    """
    Runs profile mismatch analysis on given account_ids only.
    Reuses profile detector logic but scoped to specific accounts.
    """
    from collections import defaultdict

    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in account_ids)
    cursor.execute(f'''
        SELECT txn_id, from_account, to_account, amount, timestamp, channel
        FROM Transactions
        WHERE status = 'COMPLETED'
          AND (from_account IN ({placeholders}) OR to_account IN ({placeholders}))
    ''', (*account_ids, *account_ids))

    rows = cursor.fetchall()

    account_txns = defaultdict(list)
    for row in rows:
        txn_id, from_acc, to_acc, amount, timestamp, channel = row
        txn = {
            "txn_id": txn_id,
            "from_account": from_acc,
            "to_account": to_acc,
            "amount": amount,
            "timestamp": timestamp,
            "channel": channel
        }
        account_txns[from_acc].append(txn)
        account_txns[to_acc].append(txn)

    cursor.execute(f'''
        SELECT account_id, profile_type, declared_annual_income
        FROM Accounts
        WHERE account_id IN ({placeholders})
    ''', account_ids)

    accounts = cursor.fetchall()

    findings = []
    log_steps = []

    for acc_id, profile_type, declared_income in accounts:
        txns = account_txns.get(acc_id, [])
        if len(txns) < 5:
            continue

        benchmark = BENCHMARKS.get(profile_type)
        if not benchmark:
            continue

        features = _compute_features(acc_id, txns)
        if not features:
            continue

        zscores = {
            feature: _zscore(features[feature], benchmark[feature])
            for feature in benchmark
        }

        avg_zscore = sum(zscores.values()) / len(zscores)

        log_steps.append(f"Account {acc_id} ({profile_type}): avg z-score = {avg_zscore:.2f}")

        if avg_zscore < 2.5:
            continue

        top_deviations = sorted(zscores.items(), key=lambda x: x[1], reverse=True)[:3]
        deviation_text = ", ".join(f"{k} z={v:.1f}" for k, v in top_deviations)

        findings.append({
            "type": "profile_mismatch",
            "account": acc_id,
            "profile_type": profile_type,
            "declared_income": declared_income,
            "avg_zscore": round(avg_zscore, 2),
            "top_deviations": deviation_text,
            "detail": (
                f"Account {acc_id} declared as {profile_type} "
                f"but behaves significantly outside peer group — {deviation_text}"
            ),
            "score": 25
        })

    return {
        "agent": "profile_agent",
        "findings": findings,
        "log": " | ".join(log_steps) if log_steps else "No profile mismatches found in scoped accounts"
    }