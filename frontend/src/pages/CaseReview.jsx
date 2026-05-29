import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

const API = "http://localhost:8000";

export default function CaseReview() {
  const { caseId } = useParams();
  const navigate = useNavigate();

  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [investigatorName, setInvestigatorName] = useState("");
  const [signed, setSigned] = useState(false);
  const [signing, setSigning] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(false);

  useEffect(() => {
    fetch(`${API}/case/${caseId}`)
      .then((r) => r.json())
      .then((data) => {
        setCaseData(data);
        setSigned(data.narrative_status === "SIGNED");
        setLoading(false);
      });
  }, [caseId]);

  const handleSign = async () => {
    if (!investigatorName.trim()) {
      alert("Please enter your name before signing.");
      return;
    }
    setSigning(true);
    const res = await fetch(`${API}/case/${caseId}/sign`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ investigator_name: investigatorName }),
    });
    const data = await res.json();
    setSigned(true);
    setSigning(false);
    setCaseData((prev) => ({ ...prev, narrative_status: "SIGNED", investigator_name: investigatorName }));
  };

  const handleGenerate = async () => {
    if (!signed) {
      alert("You must review and sign before generating the FIU package.");
      return;
    }
    setGenerating(true);
    const res = await fetch(`${API}/case/${caseId}/generate-fiu`, { method: "POST" });
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `FIU_${caseId}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
    setGenerating(false);
    setGenerated(true);
  };

  if (loading) return <div style={{ padding: "40px", color: "#64748b" }}>Loading case...</div>;

  const scoreBreakdown = typeof caseData.score_breakdown === "string"
    ? JSON.parse(caseData.score_breakdown)
    : caseData.score_breakdown || [];

  const agentFindings = typeof caseData.agent_findings === "string"
    ? JSON.parse(caseData.agent_findings)
    : caseData.agent_findings || [];

  return (
    <div style={{ padding: "28px", maxWidth: "900px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "28px" }}>
        <button
          onClick={() => navigate("/")}
          style={{ background: "#1e2530", border: "none", color: "#94a3b8", padding: "8px 14px", borderRadius: "6px", cursor: "pointer" }}
        >
          ← Back
        </button>
        <div>
          <div style={{ fontSize: "20px", fontWeight: 700 }}>Case Review — {caseId}</div>
          <div style={{ fontSize: "12px", color: "#64748b", marginTop: "2px" }}>
            Review the AI-assisted draft before generating the FIU evidence package
          </div>
        </div>
      </div>

      {/* Warning banner */}
      <div style={{ background: "#422006", border: "1px solid #92400e", borderRadius: "8px", padding: "12px 16px", marginBottom: "20px", fontSize: "13px", color: "#fbbf24" }}>
        ⚠ AI-Assisted Draft — Human Review Required Before Submission. The investigator is the legal accountable party.
      </div>

      {/* Risk score */}
      <div style={{ background: "#1e2530", borderRadius: "10px", padding: "20px", marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "14px" }}>Risk Score</div>
        <div style={{ fontSize: "36px", fontWeight: 700, color: caseData.risk_score >= 70 ? "#ef4444" : "#f59e0b", marginBottom: "16px" }}>
          {caseData.risk_score} / 100
        </div>
        <div style={{ fontSize: "12px", color: "#64748b", marginBottom: "10px" }}>Point Breakdown</div>
        {scoreBreakdown.map((item, i) => (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #2d3748", fontSize: "12px" }}>
            <span style={{ color: "#94a3b8" }}>{item.component}</span>
            <div style={{ textAlign: "right" }}>
              <span style={{ color: "#60a5fa", fontWeight: 600 }}>+{item.points} pts</span>
              <div style={{ color: "#475569", fontSize: "11px" }}>{item.basis}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Agent findings summary */}
      <div style={{ background: "#1e2530", borderRadius: "10px", padding: "20px", marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "14px" }}>Agent Findings</div>
        {agentFindings.map((agent, i) => (
          <div key={i} style={{ marginBottom: "12px" }}>
            <div style={{ fontSize: "12px", fontWeight: 600, color: "#60a5fa", marginBottom: "6px" }}>
              {agent.agent?.replace(/_/g, " ").toUpperCase()}
            </div>
            {agent.findings?.length === 0 && (
              <div style={{ fontSize: "12px", color: "#64748b" }}>No findings.</div>
            )}
            {agent.findings?.map((f, j) => (
              <div key={j} style={{ background: "#263040", borderRadius: "6px", padding: "8px 12px", marginBottom: "6px", fontSize: "12px", color: "#94a3b8" }}>
                {f.detail}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Narrative draft */}
      <div style={{ background: "#1e2530", borderRadius: "10px", padding: "20px", marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "12px" }}>
          Investigation Narrative
          <span style={{ marginLeft: "10px", fontSize: "11px", color: "#f59e0b", fontWeight: 400 }}>AI-generated draft</span>
        </div>
        <div style={{
          background: "#0f1117",
          borderRadius: "6px",
          padding: "16px",
          fontSize: "13px",
          color: "#cbd5e1",
          lineHeight: "1.7",
          whiteSpace: "pre-wrap",
          minHeight: "120px"
        }}>
          {caseData.narrative_draft || "Narrative not yet generated. Generate FIU package to create narrative."}
        </div>
      </div>

      {/* Human sign-off */}
      <div style={{ background: "#1e2530", borderRadius: "10px", padding: "20px", marginBottom: "20px" }}>
        <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "14px" }}>Investigator Sign-Off</div>

        {signed ? (
          <div style={{ color: "#10b981", fontSize: "14px", fontWeight: 600 }}>
            ✓ Signed by {caseData.investigator_name} — {caseData.signed_at?.slice(0, 16).replace("T", " ")}
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div style={{ fontSize: "13px", color: "#94a3b8" }}>
              By signing, you confirm you have reviewed and verified all findings above and take legal responsibility for this report.
            </div>
            <input
              type="text"
              placeholder="Enter your full name"
              value={investigatorName}
              onChange={(e) => setInvestigatorName(e.target.value)}
              style={{
                background: "#0f1117",
                border: "1px solid #334155",
                borderRadius: "6px",
                padding: "10px 14px",
                color: "#e2e8f0",
                fontSize: "13px",
                width: "300px",
                outline: "none"
              }}
            />
            <label style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", color: "#94a3b8", cursor: "pointer" }}>
              <input
                type="checkbox"
                onChange={(e) => { if (e.target.checked && investigatorName.trim()) handleSign(); }}
                disabled={signing}
                style={{ width: "16px", height: "16px" }}
              />
              I have reviewed and verified this report
            </label>
          </div>
        )}
      </div>

      {/* Generate FIU package */}
      <button
        onClick={handleGenerate}
        disabled={!signed || generating}
        style={{
          background: signed ? "#16a34a" : "#1e2530",
          border: "none",
          color: signed ? "#fff" : "#475569",
          padding: "14px 28px",
          borderRadius: "8px",
          fontSize: "15px",
          fontWeight: 700,
          cursor: signed ? "pointer" : "not-allowed",
          width: "100%",
        }}
      >
        {generating ? "Generating PDF..." : generated ? "✓ FIU Package Downloaded" : "Generate FIU Evidence Package"}
      </button>
    </div>
  );
}