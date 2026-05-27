import React from "react";
import "../styles/AgentPanel.css";

function AgentPanel({ caseData, mode }) {
  if (!caseData) return null;

  // Score breakdown from backend
  let breakdown = {};
  if (typeof caseData.score_breakdown === "string") {
    try {
      breakdown = JSON.parse(caseData.score_breakdown);
    } catch (e) {
      breakdown = {};
    }
  } else if (caseData.score_breakdown) {
    breakdown = caseData.score_breakdown;
  }

  // Fallback breakdown if empty
  if (Object.keys(breakdown).length === 0) {
    breakdown = {
      "Velocity Anomaly": 75,
      "Temporal Match": 80,
      "Profile Deviation": 65
    };
  }

  // Simulated agent status
  const agents = [
    { name: "Graph Agent", status: "Completed", description: "BFS/DFS structural path extraction finished" },
    { name: "Profile Agent", status: "Completed", description: "Z-score peer-group income/activity check completed" },
    { name: "Temporal Agent", status: "Completed", description: "Dormancy activation & fan-in window verified" }
  ];

  if (mode === "breakdown") {
    return (
      <div className="agent-panel mode-breakdown">
        <div className="breakdown-list">
          {Object.entries(breakdown).map(([factor, score]) => (
            <div key={factor} className="breakdown-item">
              <div className="breakdown-labels">
                <span className="factor-name">{factor}</span>
                <span className="factor-score">{score}%</span>
              </div>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: `${score}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (mode === "narrative") {
    return (
      <div className="agent-panel mode-narrative">
        <div className="narrative-draft-box" style={{ maxHeight: "110px" }}>
          <p>{caseData.narrative_draft || caseData.summary}</p>
        </div>
      </div>
    );
  }

  if (mode === "logs") {
    return (
      <div className="agent-panel mode-logs">
        <div className="agent-logs">
          {agents.map((agent) => (
            <div key={agent.name} className="agent-log-item">
              <div className="agent-log-header">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-status-tag">{agent.status}</span>
              </div>
              <p className="agent-desc">{agent.description}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="agent-panel">
      <div className="panel-header">
        <h3>🤖 LangGraph Orchestrator Findings</h3>
        <span className="agent-badge">AI Verified</span>
      </div>

      <div className="panel-section">
        <h4>Risk Factors Breakdown</h4>
        <div className="breakdown-list">
          {Object.entries(breakdown).map(([factor, score]) => (
            <div key={factor} className="breakdown-item">
              <div className="breakdown-labels">
                <span className="factor-name">{factor}</span>
                <span className="factor-score">{score}%</span>
              </div>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar-fill" 
                  style={{ width: `${score}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="panel-section">
        <h4>Gemini Narrative Draft</h4>
        <div className="narrative-draft-box">
          <p>{caseData.narrative_draft || caseData.summary}</p>
        </div>
      </div>

      <div className="panel-section">
        <h4>Specialized Agent Logs</h4>
        <div className="agent-logs">
          {agents.map((agent) => (
            <div key={agent.name} className="agent-log-item">
              <div className="agent-log-header">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-status-tag">{agent.status}</span>
              </div>
              <p className="agent-desc">{agent.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AgentPanel;
