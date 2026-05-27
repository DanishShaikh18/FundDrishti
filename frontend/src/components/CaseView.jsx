import "../styles/CaseView.css";

function CaseView({ caseData, mode }) {
  if (!caseData) {
    return <div className="case-view empty">No case data available</div>;
  }

  if (mode === "metrics") {
    return (
      <div className="case-view-combined mode-metrics">
        <div className="metrics-grid">
          <div className="metric">
            <span className="metric-label">Risk Score</span>
            <span className="metric-value">{caseData.score}/100</span>
          </div>
          <div className="metric">
            <span className="metric-label">Status</span>
            <span className={`metric-value status-${(caseData.status || "Open").toLowerCase()}`}>
              {caseData.status}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Created</span>
            <span className="metric-value">
              {new Date(caseData.created_at).toLocaleDateString()}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Last Updated</span>
            <span className="metric-value">
              {new Date(caseData.updated_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (mode === "accounts") {
    return (
      <div className="case-view-combined mode-accounts">
        <div className="accounts-scroll-list">
          {caseData.accounts?.map((account) => (
            <div
              key={account.id}
              className={`account-card role-${(account.role || "Suspect").toLowerCase()}`}
            >
              <div className="account-card-header">
                <span className="account-name">{account.name}</span>
                <span className="account-role">{account.role || "Suspect"}</span>
              </div>
              <div className="account-id">{account.id}</div>
              <div className="account-details-row">
                <span className="account-profile-type">{account.profile_type}</span>
                <span className="account-transactions">
                  {account.transactions_count} Transactions
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="case-view-combined">
      {/* Top Part: Risk Metrics */}
      <div className="metrics-section">
        <h3>Risk Metrics</h3>
        <div className="metrics-grid">
          <div className="metric">
            <span className="metric-label">Risk Score</span>
            <span className="metric-value">{caseData.score}/100</span>
          </div>
          <div className="metric">
            <span className="metric-label">Status</span>
            <span className={`metric-value status-${(caseData.status || "Open").toLowerCase()}`}>
              {caseData.status}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Created</span>
            <span className="metric-value">
              {new Date(caseData.created_at).toLocaleDateString()}
            </span>
          </div>
          <div className="metric">
            <span className="metric-label">Last Updated</span>
            <span className="metric-value">
              {new Date(caseData.updated_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>

      {/* Bottom Part: Scrollable Accounts Involved */}
      <div className="accounts-section">
        <h3>Accounts Involved ({caseData.accounts?.length || 0})</h3>
        <div className="accounts-scroll-list">
          {caseData.accounts?.map((account) => (
            <div
              key={account.id}
              className={`account-card role-${(account.role || "Suspect").toLowerCase()}`}
            >
              <div className="account-card-header">
                <span className="account-name">{account.name}</span>
                <span className="account-role">{account.role || "Suspect"}</span>
              </div>
              <div className="account-id">{account.id}</div>
              <div className="account-details-row">
                <span className="account-profile-type">{account.profile_type}</span>
                <span className="account-transactions">
                  {account.transactions_count} Transactions
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default CaseView;
