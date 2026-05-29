import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import cytoscape from "cytoscape";

const API = "http://localhost:8000";

const PATTERN_COLORS = {
  structuring: "#f59e0b",
  layering: "#ef4444",
  round_trip: "#8b5cf6",
  dormant_activation: "#06b6d4",
  profile_mismatch: "#10b981",
};

export default function Investigation() {
  const { patternType, accounts } = useParams();
  const navigate = useNavigate();
  const cyRef = useRef(null);
  const cyInstance = useRef(null);

  const [investigation, setInvestigation] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [replayIndex, setReplayIndex] = useState(-1);
  const [replaying, setReplaying] = useState(false);

  const accountList = accounts.split(",");

  useEffect(() => {
    fetch(`${API}/investigate?pattern_type=${patternType}&accounts=${accounts}`)
      .then((r) => r.json())
      .then((data) => {
        setInvestigation(data);
        // Extract all transactions from agent findings
        const txns = [];
        data.agent_findings?.forEach((agent) => {
          agent.findings?.forEach((f) => {
            f.transactions?.forEach((t) => {
              if (!txns.find((x) => x.txn_id === t.txn_id)) txns.push(t);
            });
          });
        });
        txns.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
        setTransactions(txns);
        setLoading(false);
      });
  }, [patternType, accounts]);

  // Build Cytoscape graph
  useEffect(() => {
    if (!investigation || !cyRef.current) return;

    const elements = [];
    const addedNodes = new Set();

    transactions.forEach((t) => {
      if (!addedNodes.has(t.from_account)) {
        elements.push({
          data: {
            id: t.from_account,
            label: t.from_account.slice(0, 12),
            flagged: accountList.includes(t.from_account),
          },
        });
        addedNodes.add(t.from_account);
      }
      if (!addedNodes.has(t.to_account)) {
        elements.push({
          data: {
            id: t.to_account,
            label: t.to_account.slice(0, 12),
            flagged: accountList.includes(t.to_account),
          },
        });
        addedNodes.add(t.to_account);
      }
      elements.push({
        data: {
          id: t.txn_id,
          source: t.from_account,
          target: t.to_account,
          amount: t.amount,
          timestamp: t.timestamp,
          channel: t.channel,
          label: `₹${(t.amount / 100000).toFixed(1)}L`,
        },
      });
    });

    if (cyInstance.current) cyInstance.current.destroy();

    cyInstance.current = cytoscape({
      container: cyRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#1e2530",
            "border-color": "#60a5fa",
            "border-width": 2,
            color: "#e2e8f0",
            label: "data(label)",
            "text-valign": "bottom",
            "text-halign": "center",
            "font-size": "10px",
            width: 40,
            height: 40,
          },
        },
        {
          selector: "node[?flagged]",
          style: {
            "background-color": "#7f1d1d",
            "border-color": "#ef4444",
            "border-width": 3,
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#334155",
            "target-arrow-color": "#334155",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            "font-size": "9px",
            color: "#94a3b8",
            "text-background-color": "#0f1117",
            "text-background-opacity": 1,
            "text-background-padding": "2px",
          },
        },
        {
          selector: "edge.highlighted",
          style: {
            "line-color": "#f59e0b",
            "target-arrow-color": "#f59e0b",
            width: 3,
          },
        },
      ],
      layout: { name: "cose", padding: 40, animate: false },
    });
  }, [investigation, transactions]);

  // Crime Scene Replay
  const startReplay = () => {
    if (!cyInstance.current || transactions.length === 0) return;
    cyInstance.current.edges().removeClass("highlighted");
    setReplaying(true);
    setReplayIndex(0);

    let i = 0;
    const interval = setInterval(() => {
      if (i >= transactions.length) {
        clearInterval(interval);
        setReplaying(false);
        return;
      }
      const txn = transactions[i];
      cyInstance.current.getElementById(txn.txn_id).addClass("highlighted");
      setReplayIndex(i);
      i++;
    }, 800);
  };

  if (loading) return <div style={{ padding: "40px", color: "#64748b" }}>Running investigation...</div>;

  const color = PATTERN_COLORS[patternType] || "#60a5fa";

  return (
    <div style={{ padding: "28px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "24px" }}>
        <button
          onClick={() => navigate("/")}
          style={{ background: "#1e2530", border: "none", color: "#94a3b8", padding: "8px 14px", borderRadius: "6px", cursor: "pointer" }}
        >
          ← Back
        </button>
        <div>
          <span style={{
            background: color + "22", color, padding: "4px 12px",
            borderRadius: "12px", fontSize: "12px", fontWeight: 700,
          }}>
            {patternType.replace(/_/g, " ").toUpperCase()}
          </span>
          <span style={{ marginLeft: "12px", fontSize: "22px", fontWeight: 700 }}>
            Risk Score: <span style={{ color: investigation.risk_score >= 70 ? "#ef4444" : "#f59e0b" }}>
              {investigation.risk_score}/100
            </span>
          </span>
        </div>
        <button
          onClick={() => navigate(`/case/${investigation.case_id}`)}
          style={{ marginLeft: "auto", background: "#2563eb", border: "none", color: "#fff", padding: "10px 20px", borderRadius: "8px", cursor: "pointer", fontWeight: 600 }}
        >
          Generate FIU Package →
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: "20px" }}>
        {/* Left — Graph */}
        <div style={{ background: "#1e2530", borderRadius: "10px", overflow: "hidden" }}>
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #2d3748", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontWeight: 600, fontSize: "14px" }}>Transaction Graph</span>
            <button
              onClick={startReplay}
              disabled={replaying}
              style={{ background: replaying ? "#334155" : "#7c3aed", border: "none", color: "#fff", padding: "6px 14px", borderRadius: "6px", cursor: replaying ? "default" : "pointer", fontSize: "12px" }}
            >
              {replaying ? `Replaying ${replayIndex + 1}/${transactions.length}...` : "▶ Crime Scene Replay"}
            </button>
          </div>
          <div ref={cyRef} style={{ height: "440px", width: "100%" }} />
        </div>

        {/* Right — Agent Findings */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {/* Score breakdown */}
          <div style={{ background: "#1e2530", borderRadius: "10px", padding: "16px" }}>
            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "12px" }}>Score Breakdown</div>
            {investigation.score_breakdown?.map((item, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #2d3748", fontSize: "12px" }}>
                <span style={{ color: "#94a3b8" }}>{item.component}</span>
                <span style={{ color: "#60a5fa", fontWeight: 600 }}>+{item.points}</span>
              </div>
            ))}
          </div>

          {/* Agent findings */}
          {investigation.agent_findings?.map((agent, i) => (
            <div key={i} style={{ background: "#1e2530", borderRadius: "10px", padding: "16px" }}>
              <div style={{ fontWeight: 600, fontSize: "13px", color: "#60a5fa", marginBottom: "8px" }}>
                {agent.agent?.replace("_", " ").toUpperCase()}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "8px", fontStyle: "italic" }}>
                {agent.log}
              </div>
              {agent.findings?.map((f, j) => (
                <div key={j} style={{ background: "#263040", borderRadius: "6px", padding: "8px 10px", marginBottom: "6px", fontSize: "12px" }}>
                  <div style={{ color: "#e2e8f0", marginBottom: "2px" }}>{f.type?.replace(/_/g, " ")}</div>
                  <div style={{ color: "#94a3b8" }}>{f.detail}</div>
                </div>
              ))}
              {agent.findings?.length === 0 && (
                <div style={{ color: "#64748b", fontSize: "12px" }}>No findings from this agent.</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div style={{ marginTop: "20px", background: "#1e2530", borderRadius: "10px", padding: "16px" }}>
        <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "12px" }}>Transaction Timeline</div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
            <thead>
              <tr style={{ color: "#64748b", borderBottom: "1px solid #2d3748" }}>
                {["#", "Time", "From", "To", "Amount", "Channel"].map((h) => (
                  <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {transactions.map((t, i) => (
                <tr
                  key={t.txn_id}
                  style={{
                    borderBottom: "1px solid #2d3748",
                    background: replayIndex >= i ? "#1a2540" : "transparent",
                    transition: "background 0.3s"
                  }}
                >
                  <td style={{ padding: "8px 12px", color: "#64748b" }}>{i + 1}</td>
                  <td style={{ padding: "8px 12px", color: "#94a3b8" }}>{t.timestamp.replace("T", " ").slice(0, 16)}</td>
                  <td style={{ padding: "8px 12px", color: "#e2e8f0" }}>{t.from_account.slice(0, 14)}</td>
                  <td style={{ padding: "8px 12px", color: "#e2e8f0" }}>{t.to_account.slice(0, 14)}</td>
                  <td style={{ padding: "8px 12px", color: "#10b981", fontWeight: 600 }}>₹{t.amount.toLocaleString("en-IN")}</td>
                  <td style={{ padding: "8px 12px", color: "#94a3b8" }}>{t.channel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}