import uuid
from datetime import datetime
from database import get_connection
from agents.graph_agent import run_graph_agent
from agents.profile_agent import run_profile_agent
from agents.temporal_agent import run_temporal_agent

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

def _scope_and_run(conn, pattern_type, accounts_involved):
    """
    Core adaptive scoping logic.
    Decides which agents run on which subgraph based on pattern type.
    """
    cursor = conn.cursor()
    log = []
    agent_results = []

    if pattern_type == "structuring":
        # Fan out from hub — find 2nd degree neighbors
        placeholders = ",".join("?" for _ in accounts_involved)
        cursor.execute(f'''
            SELECT DISTINCT from_account FROM Transactions
            WHERE to_account IN ({placeholders}) AND status = 'COMPLETED'
        ''', accounts_involved)
        neighbors = [row[0] for row in cursor.fetchall()]
        scoped_accounts = list(set(accounts_involved + neighbors))
        log.append(f"Structuring: scoped to {len(scoped_accounts)} accounts including 2nd-degree neighbors")

        graph_result = run_graph_agent(conn, scoped_accounts)
        profile_result = run_profile_agent(conn, scoped_accounts)
        agent_results = [graph_result, profile_result]

    elif pattern_type == "layering":
        # Scope temporal agent to the chain's time window only
        placeholders = ",".join("?" for _ in accounts_involved)
        cursor.execute(f'''
            SELECT MIN(timestamp), MAX(timestamp) FROM Transactions
            WHERE (from_account IN ({placeholders}) OR to_account IN ({placeholders}))
              AND status = 'COMPLETED'
        ''', (*accounts_involved, *accounts_involved))
        row = cursor.fetchone()
        log.append(f"Layering: temporal agent scoped to window {row[0]} — {row[1]}")

        graph_result = run_graph_agent(conn, accounts_involved)
        temporal_result = run_temporal_agent(conn, accounts_involved, window_hours=2)
        agent_results = [graph_result, temporal_result]

    elif pattern_type == "round_trip":
        # Cycle detected — run graph + temporal on cycle accounts only
        log.append(f"Round-trip: graph and temporal agents scoped to {len(accounts_involved)} cycle accounts")

        graph_result = run_graph_agent(conn, accounts_involved)
        temporal_result = run_temporal_agent(conn, accounts_involved, window_hours=72)
        agent_results = [graph_result, temporal_result]

    elif pattern_type == "dormant_activation":
        # Run temporal agent bank-wide in cluster mode
        log.append("Dormant activation: temporal agent running bank-wide in cluster mode")

        temporal_result = run_temporal_agent(conn, accounts_involved, cluster_mode=True)
        profile_result = run_profile_agent(conn, accounts_involved)
        agent_results = [temporal_result, profile_result]

    elif pattern_type == "profile_mismatch":
        # Profile mismatch — run profile + graph on account and its neighbors
        placeholders = ",".join("?" for _ in accounts_involved)
        cursor.execute(f'''
            SELECT DISTINCT to_account FROM Transactions
            WHERE from_account IN ({placeholders}) AND status = 'COMPLETED'
            UNION
            SELECT DISTINCT from_account FROM Transactions
            WHERE to_account IN ({placeholders}) AND status = 'COMPLETED'
        ''', (*accounts_involved, *accounts_involved))
        neighbors = [row[0] for row in cursor.fetchall()]
        scoped_accounts = list(set(accounts_involved + neighbors))
        log.append(f"Profile mismatch: scoped to account + {len(neighbors)} neighbors")

        profile_result = run_profile_agent(conn, scoped_accounts)
        graph_result = run_graph_agent(conn, scoped_accounts)
        agent_results = [profile_result, graph_result]

    else:
        log.append(f"Unknown pattern type: {pattern_type} — running all agents")
        agent_results = [
            run_graph_agent(conn, accounts_involved),
            run_profile_agent(conn, accounts_involved),
            run_temporal_agent(conn, accounts_involved)
        ]

    return agent_results, log


def _compute_score(agent_results, base_score_contribution):
    """
    Combines agent findings into a single 0-100 score.
    Base score comes from the detector that triggered the alert.
    Agent findings add on top.
    """
    total = base_score_contribution
    breakdown = [f"Detector finding: {base_score_contribution} pts"]

    for result in agent_results:
        for finding in result.get("findings", []):
            pts = finding.get("score", 0)
            if pts > 0:
                total += pts
                breakdown.append(f"{finding['type']}: +{pts} pts")

    total = min(total, 100)
    return total, breakdown


def investigate(pattern_type, accounts_involved, base_score_contribution=35):
    """
    Main entry point. Called from FastAPI.
    Returns full investigation result including agent findings,
    score, breakdown, and execution log.
    """
    conn = get_connection()

    # Run adaptive agents
    agent_results, scope_log = _scope_and_run(conn, pattern_type, accounts_involved)

    # Compute score
    risk_score, score_breakdown = _compute_score(agent_results, base_score_contribution)

    # Build execution log
    execution_log = scope_log.copy()
    for result in agent_results:
        execution_log.append(f"[{result['agent']}] {result['log']}")

    # Save case to database
    case_id = f"CASE_{uuid.uuid4().hex[:8].upper()}"
    cursor = conn.cursor()
    import json
    cursor.execute('''
        INSERT INTO Cases (case_id, alert_id, risk_score, score_breakdown, agent_findings, narrative_status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        case_id,
        None,
        risk_score,
        json.dumps(score_breakdown),
        json.dumps(agent_results),
        "DRAFT"
    ))
    conn.commit()
    conn.close()

    return {
        "case_id": case_id,
        "pattern_type": pattern_type,
        "accounts_involved": accounts_involved,
        "risk_score": risk_score,
        "score_breakdown": score_breakdown,
        "agent_findings": agent_results,
        "execution_log": execution_log,
        "investigated_at": datetime.now().isoformat()
    }