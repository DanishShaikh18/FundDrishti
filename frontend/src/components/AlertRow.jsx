import {
  formatTimestamp,
  formatCurrency,
  formatNumber,
  getStatusColor,
  getPatternLabel,
} from "../utils/formatters";
import StatusBadge from "./StatusBadge";
import "../styles/AlertRow.css";

function AlertRow({ alert, onClick }) {
  return (
    <div className="alert-row" onClick={onClick}>
      <div className="col-score">
        <div
          className={`score-badge score-${Math.round(alert.score / 10) * 10}`}
        >
          {alert.score}
        </div>
      </div>
      <div className="col-pattern">
        <span className="pattern-icon">
          {getPatternLabel(alert.pattern_type)}
        </span>
        <span className="pattern-name">{alert.pattern_type}</span>
      </div>
      <div className="col-accounts">
        <span className="accounts-badge">{alert.accounts}</span>
      </div>
      <div className="col-amount">{formatCurrency(alert.amount)}</div>
      <div className="col-timestamp">{formatTimestamp(alert.timestamp)}</div>
      <div className="col-status">
        <StatusBadge status={alert.status} />
      </div>
    </div>
  );
}

export default AlertRow;
