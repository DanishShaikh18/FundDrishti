import sqlite3
import math
from collections import defaultdict

# Profile benchmarks — expected behavioral ranges per declared profile type
BENCHMARKS = {
    "Student": {
        "txn_per_day": 0.5,
        "avg_amount": 8000,
        "unique_counterparties": 5,
        "cash_ratio": 0.3,
        "night_ratio": 0.05,
        "channel_diversity": 2
    },
    "Salaried": {
        "txn_per_day": 1.0,
        "avg_amount": 15000,
        "unique_counterparties": 15,
        "cash_ratio": 0.2,
        "night_ratio": 0.08,
        "channel_diversity": 3
    },
    "SmallBusiness": {
        "txn_per_day": 5.0,
        "avg_amount": 80000,
        "unique_counterparties": 35,
        "cash_ratio": 0.3,
        "night_ratio": 0.15,
        "channel_diversity": 4
    },
    "CashBusiness": {
        "txn_per_day": 8.0,
        "avg_amount": 150000,
        "unique_counterparties": 50,
        "cash_ratio": 0.6,
        "night_ratio": 0.25,
        "channel_diversity": 4
    }
}

Z_THRESHOLD = 2.5

def _compute_features(account_id, txns):
    if not txns:
        return None

    dates = set(t["timestamp"][:10] for t in txns)
    num_days = max(len(dates), 1)
    txn_per_day = len(txns) / num_days

    amounts = [t["amount"] for t in txns]
    avg_amount = sum(amounts) / len(amounts)

    counterparties = set()
    for t in txns:
        if t["from_account"] == account_id:
            counterparties.add(t["to_account"])
        else:
            counterparties.add(t["from_account"])
    unique_counterparties = len(counterparties)

    cash_txns = [t for t in txns if t["channel"] == "CASH"]
    cash_ratio = len(cash_txns) / len(txns)

    night_txns = [t for t in txns if int(t["timestamp"][11:13]) < 6 or int(t["timestamp"][11:13]) >= 22]
    night_ratio = len(night_txns) / len(txns)

    channels = set(t["channel"] for t in txns)
    channel_diversity = len(channels)

    return {
        "txn_per_day": txn_per_day,
        "avg_amount": avg_amount,
        "unique_counterparties": unique_counterparties,
        "cash_ratio": cash_ratio,
        "night_ratio": night_ratio,
        "channel_diversity": channel_diversity
    }

def _zscore(actual, benchmark):
    # Use benchmark as mean, 30% of benchmark as std
    std = benchmark * 0.3 if benchmark != 0 else 1
    return abs(actual - benchmark) / std

def detect_profile_mismatch(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT account_id, profile_type, declared_annual_income FROM Accounts")
    accounts = cursor.fetchall()

    cursor.execute('''
        SELECT txn_id, from_account, to_account, amount, timestamp, channel
        FROM Transactions
        WHERE status = 'COMPLETED'
    ''')
    all_txns = cursor.fetchall()

    # Group transactions per account
    account_txns = defaultdict(list)
    for row in all_txns:
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

    findings = []

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

        # Compute z-score per feature
        zscores = {
            feature: _zscore(features[feature], benchmark[feature])
            for feature in benchmark
        }

        avg_zscore = sum(zscores.values()) / len(zscores)

        if avg_zscore < Z_THRESHOLD:
            continue

        # Find worst offending features
        top_deviations = sorted(zscores.items(), key=lambda x: x[1], reverse=True)[:3]
        deviation_text = ", ".join(
            f"{k} z={v:.1f}" for k, v in top_deviations
        )

        confidence = round(min(avg_zscore / 5.0, 1.0), 2)

        findings.append({
            "pattern_type": "profile_mismatch",
            "confidence": confidence,
            "accounts_involved": [acc_id],
            "evidence": {
                "transactions": txns[:10],
                "finding": (
                    f"Account {acc_id} declared as {profile_type} "
                    f"(income ₹{declared_income:,.0f}/yr) but behavioral features "
                    f"deviate significantly from peer group — "
                    f"top deviations: {deviation_text}"
                )
            },
            "score_contribution": 25
        })

    return findings