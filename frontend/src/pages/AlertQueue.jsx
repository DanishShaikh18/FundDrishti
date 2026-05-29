import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const PATTERN_COLORS = {
  structuring: "#f59e0b",
  layering: "#ef4444",
  round_trip: "#8b5cf6",
  dormant_activation: "#06b6d4",
  profile_mismatch: "#10b981",
};

const API = "http://localhost:8000";

export default function AlertQueue() {
  const [findings, setFindings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      fetch(`${API}/detect/all`).then((r) => r.json()),
      fetch(`${API}/stats`).then((r) => r.json()),
    ]).then(([alertData, statsData]) => {
      const all = [];
      Object.entries(alertData.findings).forEach(([pattern, items]) => {
        items.forEach((item) => all.push({ ...item, pattern_type: pattern }));
      });
      all.sort((a, b) => b.confidence - a.confidence);
      setFindings(all);
      setStats(statsData);
      setLoading(false);
    });
  }, []);

  if (loading) return <div style={{ padding: "40px", color: "#64748b" }}>Loading alerts...</div>;

  return (
    <div style={{ padding: "28px" }}>
      {/* Stats bar */}
      {stats && (
        <div style={{ display: "flex", gap: "16px", marginBottom: "28px" }}>
          {[
            { label: "Total Accounts", value: stats.total_accounts },
            { label: "Total Transactions", value: stats.total_transactions },
            { label: "Fraud Cases Planted", value: stats.fraud_cases_planted },
            { label: "Active Alerts", value: findings.length },
          ].map((s) => (
            <div key={s.label} style={{ background: "#1e2530", borderRadius: "8px", padding: "16px 24px", flex: 1 }}>
              <div style={{ fontSize: "24px", fontWeight: 700, color: "#60a5fa" }}>{s.value}</div>
              <div style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Title */}
      <div style={{ marginBottom: "16px", fontSize: "16px", fontWeight: 600 }}>
        Alert Queue <span style={{ color: "#64748b", fontWeight: 400, fontSize: "13px" }}>— click any alert to investigate</span>
      </div>

      {/* Table */}
      <div style={{ background: "#1e2530", borderRadius: "10px", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #2d3748", color: "#64748b" }}>
              {["Pattern", "Accounts Involved", "Confidence", "Finding"].map((h) => (
                <th key={h} style={{ padding: "12px 16px", textAlign: "left", fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {findings.length === 0 && (
              <tr>
                <td colSpan={4} style={{ padding: "32px", textAlign: "center", color: "#64748b" }}>
                  No alerts found. Run detectors first.
                </td>
              </tr>
            )}
            {findings.map((f, i) => (
              <tr
                key={i}
                onClick={() => navigate(`/investigate/${f.pattern_type}/${f.accounts_involved.join(",")}`)}
                style={{
                  borderBottom: "1px solid #2d3748",
                  cursor: "pointer",
                  transition: "background 0.15s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "#263040")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              >
                <td style={{ padding: "12px 16px" }}>
                  <span style={{
                    background: PATTERN_COLORS[f.pattern_type] + "22",
                    color: PATTERN_COLORS[f.pattern_type],
                    padding: "3px 10px",
                    borderRadius: "12px",
                    fontSize: "12px",
                    fontWeight: 600,
                  }}>
                    {f.pattern_type.replace("_", " ").toUpperCase()}
                  </span>
                </td>
                <td style={{ padding: "12px 16px", color: "#94a3b8" }}>
                  {f.accounts_involved.slice(0, 3).join(", ")}
                  {f.accounts_involved.length > 3 && ` +${f.accounts_involved.length - 3} more`}
                </td>
                <td style={{ padding: "12px 16px" }}>
                  <span style={{ color: f.confidence >= 0.8 ? "#ef4444" : f.confidence >= 0.6 ? "#f59e0b" : "#10b981" }}>
                    {(f.confidence * 100).toFixed(0)}%
                  </span>
                </td>
                <td style={{ padding: "12px 16px", color: "#94a3b8", maxWidth: "340px" }}>
                  <span style={{ overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 1, WebkitBoxOrient: "vertical" }}>
                    {f.evidence?.finding}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}