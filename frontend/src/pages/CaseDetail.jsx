import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useCaseDetail } from "../hooks/useCaseDetail";
import { updateCaseStatus } from "../services/api";
import axios from "axios";
import CaseView from "../components/CaseView";
import TransactionGraph from "../components/TransactionGraph";
import BehavioralRadar from "../components/BehavioralRadar";
import AgentPanel from "../components/AgentPanel";
import Timeline from "../components/Timeline";
import "../styles/CaseDetail.css";

function CaseDetail() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const { caseData, loading, error, refetch } = useCaseDetail(caseId);
  const [updating, setUpdating] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState("");
  const [investigatorName, setInvestigatorName] = useState("");
  const [verified, setVerified] = useState(false);
  const [generatingFiu, setGeneratingFiu] = useState(false);
  const [fiuResult, setFiuResult] = useState(null);

  // Sync state with loaded data
  React.useEffect(() => {
    if (caseData) {
      setSelectedStatus(caseData.status);
      if (caseData.investigator_name) {
        setInvestigatorName(caseData.investigator_name);
      }
      if (caseData.fiu_generated) {
        setFiuResult({
          success: true,
          download_pdf: `/downloads/${caseId}_FIU_Report.pdf`,
          download_xml: `/downloads/${caseId}_goAML_Package.xml`,
          signed_at: caseData.signed_at,
          investigator: caseData.investigator_name
        });
      }
    }
  }, [caseData, caseId]);

  const handleStatusChange = async (newStatus) => {
    try {
      setUpdating(true);
      await updateCaseStatus(caseId, newStatus);
      setSelectedStatus(newStatus);
      refetch();
    } catch (err) {
      console.error("Failed to update status:", err);
    } finally {
      setUpdating(false);
    }
  };

  const handleGenerateFiu = async (e) => {
    e.preventDefault();
    if (!investigatorName || !verified) return;

    setGeneratingFiu(true);
    try {
      // Direct call to API
      const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await axios.post(`${API_BASE_URL}/alert/${caseId}/generate-fiu`, {
        investigator_name: investigatorName,
        verified: true
      });
      setFiuResult(response.data);
      setSelectedStatus("Closed");
      refetch();
    } catch (err) {
      console.error("Failed to generate FIU Package:", err);
      alert("Error generating FIU Package. Please make sure the backend is running.");
    } finally {
      setGeneratingFiu(false);
    }
  };

  if (error) {
    return (
      <div className="case-detail error-container">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          ← Back to Dashboard
        </button>
        <div className="error">
          <p className="error-message">Failed to load case: {error}</p>
        </div>
      </div>
    );
  }

  if (loading || !caseData) {
    return (
      <div className="case-detail loading-container">
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          ← Back to Dashboard
        </button>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading case investigation file...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="case-detail-viewport">
      {/* Global Status Bar (Fixed at top) */}
      <header className="case-header">
        <div className="header-left">
          <button className="back-button" onClick={() => navigate("/dashboard")}>
            ← Alert Queue
          </button>
          <div className="header-title-block">
            <span className="case-id-tag">Case File</span>
            <h1>{caseId}</h1>
          </div>
        </div>
        <div className="header-right">
          <div className="risk-display">
            <span className="risk-label">Risk Severity</span>
            <div className={`risk-value-pill score-${Math.round(caseData.score / 10) * 10}`}>
              {caseData.score}/100
            </div>
          </div>
          <div className="status-control">
            <label>Investigation Status</label>
            <select
              value={selectedStatus}
              onChange={(e) => handleStatusChange(e.target.value)}
              disabled={updating || caseData.fiu_generated}
            >
              <option value="Open">Open</option>
              <option value="Investigating">Investigating</option>
              <option value="Closed">Closed</option>
            </select>
          </div>
        </div>
      </header>

      {/* Core Bento Grid (Three-column data grid) */}
      <main className="case-content">
        <div className="case-grid">
          
          {/* Bento Cell 1: Interactive Fund Flow (Spans 2 columns, spans 1 row) */}
          <section className="detail-section section-graph">
            <div className="section-header">
              <h2>🌐 Interactive Fund Flow Network</h2>
              <span className="info-tip">Nodes color-coded by role (Red: Suspect, Blue: Victim, Orange: Intermediary)</span>
            </div>
            <div className="graph-wrapper">
              {caseData.transaction_subgraph ? (
                <TransactionGraph
                  nodes={caseData.transaction_subgraph.nodes}
                  edges={caseData.transaction_subgraph.edges}
                />
              ) : (
                <p className="empty-state">No transaction network data available</p>
              )}
            </div>
          </section>

          {/* Bento Cell 2: Behavioral Profile (Spans 1 column, spans 1 row) */}
          <section className="detail-section section-radar">
            <div className="section-header">
              <h2>📊 Behavioral Profile</h2>
              <span className="info-tip">Normalized metric deviations against base</span>
            </div>
            <div className="radar-wrapper">
              <BehavioralRadar behavioralProfile={caseData.behavioral_profile} />
            </div>
          </section>

          {/* Bento Cell 3: Chronological Transaction History (Spans 1 column, spans 2 rows) */}
          <section className="detail-section section-timeline">
            <div className="section-header">
              <h2>⏱️ Transaction History</h2>
              <span className="info-tip">Chronological flow of sub-network transfers</span>
            </div>
            <div className="timeline-scroll-area">
              <Timeline edges={caseData.transaction_subgraph?.edges} />
            </div>
          </section>

          {/* Bento Cell 4: Risk Matrix / Factors Breakdown (Row 2, Col 2) */}
          <section className="detail-section section-risk-matrix">
            <div className="section-header">
              <h2>📊 Risk Factors Breakdown</h2>
              <span className="info-tip">LangGraph analysis of anomaly vectors</span>
            </div>
            <div className="breakdown-wrapper">
              <AgentPanel caseData={caseData} mode="breakdown" />
            </div>
          </section>

          {/* Bento Cell 5: Risk Metrics (Row 2, Col 3) */}
          <section className="detail-section section-metrics">
            <div className="section-header">
              <h2>📈 Case Severity & Timing</h2>
              <span className="info-tip">Key parameters and response windows</span>
            </div>
            <div className="metrics-wrapper">
              <CaseView caseData={caseData} mode="metrics" />
            </div>
          </section>

          {/* Bento Cell 6: Specialized Agent Logs (Row 3, Col 2) */}
          <section className="detail-section section-agent-logs">
            <div className="section-header">
              <h2>🤖 Specialized Agent Logs</h2>
              <span className="info-tip">Multi-agent orchestrator operational trace</span>
            </div>
            <div className="agent-logs-wrapper">
              <AgentPanel caseData={caseData} mode="logs" />
            </div>
          </section>

          {/* Bento Cell 7: Accounts Involved (Row 3, Col 3) */}
          <section className="detail-section section-accounts">
            <div className="section-header">
              <h2>👥 Accounts Involved ({caseData.accounts?.length || 0})</h2>
              <span className="info-tip">Identified roles in sub-network</span>
            </div>
            <div className="accounts-wrapper">
              <CaseView caseData={caseData} mode="accounts" />
            </div>
          </section>

          {/* Bento Cell 8: Gemini Narrative Report (Row 4, Spans 3 columns) */}
          <section className="detail-section section-narrative">
            <div className="section-header">
              <h2>📝 Gemini Narrative Report Draft</h2>
              <span className="info-tip">Generative summary of anomalous activity patterns</span>
            </div>
            <div className="narrative-wrapper">
              <AgentPanel caseData={caseData} mode="narrative" />
            </div>
          </section>

        </div>
      </main>

      {/* Investigator Sign-off (Human-in-the-Loop Gate, fixed at bottom) */}
      <footer className="case-footer">
        <section className="footer-hitl-panel">
          <div className="hitl-header">
            <h3>⚖️ Accountability Gate (Human-in-the-Loop Verification)</h3>
            <span className="regulatory-tag">STR Compliance Gate</span>
          </div>

          {!fiuResult ? (
            <form className="hitl-form" onSubmit={handleGenerateFiu}>
              <div className="hitl-form-row">
                <div className="form-group flex-input">
                  <label htmlFor="investigator-name">Investigator Official Name *</label>
                  <input
                    type="text"
                    id="investigator-name"
                    placeholder="e.g. Inspector Sarah Connor"
                    value={investigatorName}
                    onChange={(e) => setInvestigatorName(e.target.value)}
                    required
                  />
                </div>

                <div className="form-checkbox-group flex-label">
                  <input
                    type="checkbox"
                    id="verify-checkbox"
                    checked={verified}
                    onChange={(e) => setVerified(e.target.checked)}
                    required
                  />
                  <label htmlFor="verify-checkbox">
                    I, the undersigned investigator, hereby declare that I have reviewed the graph network, AI-generated narrative draft, and customer behavioral deviations, and verify that these findings reflect my professional AML judgment.
                  </label>
                </div>

                <button
                  type="submit"
                  className="btn-submit-fiu"
                  disabled={generatingFiu || !investigatorName || !verified}
                >
                  {generatingFiu ? "Compiling Package..." : "Verify & Generate Package"}
                </button>
              </div>
            </form>
          ) : (
            <div className="fiu-success-box">
              <div className="success-header">
                <span className="success-icon">✓</span>
                <div>
                  <h4>FIU Evidence Package Compiled</h4>
                  <p className="signature-info">Signed by {fiuResult.investigator} on {new Date(fiuResult.signed_at).toLocaleString()}</p>
                </div>
              </div>

              <div className="download-buttons-horizontal">
                <a
                  href={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}${fiuResult.download_pdf}`}
                  className="btn-download pdf-btn"
                  target="_blank"
                  rel="noopener noreferrer"
                  download
                >
                  📄 Download Official PDF Report
                </a>
                <a
                  href={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}${fiuResult.download_xml}`}
                  className="btn-download xml-btn"
                  target="_blank"
                  rel="noopener noreferrer"
                  download
                >
                  ⚙️ Download goAML XML Package
                </a>
              </div>
            </div>
          )}
        </section>
      </footer>
    </div>
  );
}

export default CaseDetail;
