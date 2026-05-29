import json
import sqlite3
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def _get_training_data(conn):
    """
    Build feature matrix from Labels table.
    Features: binary flags for each pattern type detected per case.
    Target: fraud_label.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, pattern_type, accounts_involved, fraud_label FROM Labels")
    labels = cursor.fetchall()

    pattern_types = ["structuring", "layering", "round_trip", "dormant_activation", "profile_mismatch"]

    X = []
    y = []

    for case_id, pattern_type, accounts_involved, fraud_label in labels:
        # One-hot encode pattern type as binary features
        features = [1 if pattern_type == p else 0 for p in pattern_types]
        X.append(features)
        y.append(fraud_label)

    return np.array(X), np.array(y), pattern_types


def train_and_get_weights(conn):
    """
    Train Logistic Regression on labeled cases.
    Returns normalized weights (sum to 100) per pattern type.
    """
    X, y, pattern_types = _get_training_data(conn)

    if len(set(y)) < 2:
        # Fallback equal weights if labels are all same class
        equal = round(100 / len(pattern_types), 1)
        return {p: equal for p in pattern_types}

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X, y)

    # Extract coefficients — one per pattern type
    coefficients = model.coef_[0]

    # Take absolute values — direction doesn't matter, magnitude does
    abs_coefs = np.abs(coefficients)

    # Normalize to sum to 100
    total = abs_coefs.sum()
    if total == 0:
        normalized = [100 / len(pattern_types)] * len(pattern_types)
    else:
        normalized = (abs_coefs / total) * 100

    weights = {pattern_types[i]: round(float(normalized[i]), 1) for i in range(len(pattern_types))}
    return weights


def _watchlist_proximity_score(conn, accounts_involved, max_points=15):
    """
    Check if any account in the list is close to a watchlisted account.
    Returns 0-15 bonus points.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT account_id FROM Watchlist")
    watchlist = {row[0] for row in cursor.fetchall()}

    direct_hits = [a for a in accounts_involved if a in watchlist]
    if not direct_hits:
        # Check 1-hop neighbors
        placeholders = ",".join("?" for _ in accounts_involved)
        cursor.execute(f'''
            SELECT DISTINCT to_account FROM Transactions
            WHERE from_account IN ({placeholders}) AND status = 'COMPLETED'
            UNION
            SELECT DISTINCT from_account FROM Transactions
            WHERE to_account IN ({placeholders}) AND status = 'COMPLETED'
        ''', (*accounts_involved, *accounts_involved))
        neighbors = {row[0] for row in cursor.fetchall()}
        neighbor_hits = neighbors & watchlist
        if neighbor_hits:
            return 8, f"1-hop neighbor(s) {list(neighbor_hits)} are on RBI watchlist"
        return 0, "No watchlist proximity detected"

    return max_points, f"Account(s) {direct_hits} are directly on RBI watchlist"


def compute_final_score(conn, pattern_type, agent_findings, accounts_involved):
    """
    Main scoring function.
    Combines LR-derived base weight + agent finding scores + watchlist proximity.
    Returns final score (0-100) with full point-traceable breakdown.
    """
    weights = train_and_get_weights(conn)

    breakdown = []
    total = 0

    # Base score from pattern type — LR derived weight
    base_score = weights.get(pattern_type, 20)
    total += base_score
    breakdown.append({
        "component": f"Pattern detected: {pattern_type}",
        "points": round(base_score, 1),
        "basis": "Logistic Regression coefficient — most discriminative pattern in labeled dataset"
    })

    # Agent finding scores
    for agent_result in agent_findings:
        agent_name = agent_result.get("agent", "unknown")
        for finding in agent_result.get("findings", []):
            pts = finding.get("score", 0)
            if pts > 0:
                total += pts
                breakdown.append({
                    "component": f"{agent_name} — {finding['type']}",
                    "points": pts,
                    "basis": finding.get("detail", "")
                })

    # Watchlist proximity bonus
    watchlist_pts, watchlist_reason = _watchlist_proximity_score(conn, accounts_involved)
    if watchlist_pts > 0:
        total += watchlist_pts
        breakdown.append({
            "component": "Watchlist proximity",
            "points": watchlist_pts,
            "basis": watchlist_reason
        })

    final_score = round(min(total, 100), 1)

    return {
        "risk_score": final_score,
        "score_breakdown": breakdown,
        "weights_used": weights
    }