import networkx as nx
from collections import defaultdict

def run_graph_agent(conn, account_ids):
    """
    Runs graph analysis on a subgraph of given account_ids.
    Returns structured findings: hubs, fan-in, fan-out, cycles.
    """
    cursor = conn.cursor()

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
        return {"agent": "graph_agent", "findings": [], "log": "No transactions found for given accounts"}

    G = nx.DiGraph()
    for row in rows:
        txn_id, from_acc, to_acc, amount, timestamp, channel = row
        G.add_edge(from_acc, to_acc, txn_id=txn_id, amount=amount, timestamp=timestamp)

    findings = []
    log_steps = []

    # Hub detection — nodes with high in-degree
    in_degrees = dict(G.in_degree())
    hubs = {node: deg for node, deg in in_degrees.items() if deg >= 3}
    if hubs:
        log_steps.append(f"Hub detection: found {len(hubs)} hub(s) with in-degree >= 3")
        findings.append({
            "type": "hub_detected",
            "detail": f"{len(hubs)} hub account(s) found with 3+ incoming connections",
            "accounts": list(hubs.keys()),
            "score": 10
        })

    # Fan-out detection — nodes with high out-degree
    out_degrees = dict(G.out_degree())
    fan_out_nodes = {node: deg for node, deg in out_degrees.items() if deg >= 3}
    if fan_out_nodes:
        log_steps.append(f"Fan-out detection: found {len(fan_out_nodes)} node(s) with out-degree >= 3")
        findings.append({
            "type": "fan_out_detected",
            "detail": f"{len(fan_out_nodes)} account(s) sending to 3+ destinations",
            "accounts": list(fan_out_nodes.keys()),
            "score": 8
        })

    # Cycle detection
    try:
        cycles = list(nx.simple_cycles(G))
        if cycles:
            log_steps.append(f"Cycle detection: found {len(cycles)} cycle(s)")
            findings.append({
                "type": "cycle_detected",
                "detail": f"{len(cycles)} circular flow(s) detected in subgraph",
                "accounts": list({acc for cycle in cycles for acc in cycle}),
                "score": 15
            })
    except Exception:
        pass

    # Watchlist proximity
    cursor.execute("SELECT account_id FROM Watchlist")
    watchlist = {row[0] for row in cursor.fetchall()}
    flagged_neighbors = set(G.nodes()) & watchlist
    if flagged_neighbors:
        log_steps.append(f"Watchlist proximity: {len(flagged_neighbors)} watchlisted account(s) in subgraph")
        findings.append({
            "type": "watchlist_proximity",
            "detail": f"{len(flagged_neighbors)} account(s) in subgraph are on the RBI watchlist",
            "accounts": list(flagged_neighbors),
            "score": 15
        })

    return {
        "agent": "graph_agent",
        "findings": findings,
        "log": " | ".join(log_steps) if log_steps else "No significant graph patterns found"
    }