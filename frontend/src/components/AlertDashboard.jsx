import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAlerts } from "../hooks/useAlerts";
import { useAppContext } from "../context/AppContext";
import AlertRow from "./AlertRow";
import "../styles/AlertDashboard.css";

function AlertDashboard() {
  const { alerts, loading, error } = useAlerts();
  const { filters } = useAppContext();
  const navigate = useNavigate();
  const [sortBy, setSortBy] = useState("score");

  // Filter alerts based on context filters
  const filteredAlerts = alerts.filter((alert) => {
    if (filters.patternType && alert.pattern_type !== filters.patternType)
      return false;
    if (filters.status && alert.status !== filters.status) return false;
    if (alert.score < filters.minScore || alert.score > filters.maxScore)
      return false;
    return true;
  });

  // Sort alerts
  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    if (sortBy === "score") return b.score - a.score;
    if (sortBy === "timestamp")
      return new Date(b.timestamp) - new Date(a.timestamp);
    if (sortBy === "amount") return b.amount - a.amount;
    return 0;
  });

  const handleRowClick = (alert) => {
    navigate(`/case/${alert.id}`);
  };

  if (error) {
    return (
      <div className="alert-dashboard error">
        <p className="error-message">Failed to load alerts: {error}</p>
      </div>
    );
  }

  return (
    <div className="alert-dashboard">
      <div className="dashboard-header">
        <h1>🚨 Fraud Alert Queue</h1>
        <div className="sort-controls">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="score">Risk Score (High→Low)</option>
            <option value="timestamp">Latest First</option>
            <option value="amount">Amount (High→Low)</option>
          </select>
        </div>
      </div>

      <div className="alerts-stats">
        <div className="stat">
          <span className="stat-label">Total Alerts</span>
          <span className="stat-value">{filteredAlerts.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Open</span>
          <span className="stat-value open">
            {filteredAlerts.filter((a) => a.status === "Open").length}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">Investigating</span>
          <span className="stat-value investigating">
            {filteredAlerts.filter((a) => a.status === "Investigating").length}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">Closed</span>
          <span className="stat-value closed">
            {filteredAlerts.filter((a) => a.status === "Closed").length}
          </span>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading alerts...</div>
      ) : sortedAlerts.length === 0 ? (
        <div className="no-alerts">No alerts match your filters</div>
      ) : (
        <div className="alerts-table">
          <div className="table-header">
            <div className="col-score">Risk</div>
            <div className="col-pattern">Pattern</div>
            <div className="col-accounts">Accounts</div>
            <div className="col-amount">Amount</div>
            <div className="col-timestamp">Time</div>
            <div className="col-status">Status</div>
          </div>
          <div className="table-body">
            {sortedAlerts.map((alert) => (
              <AlertRow
                key={alert.id}
                alert={alert}
                onClick={() => handleRowClick(alert)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AlertDashboard;
