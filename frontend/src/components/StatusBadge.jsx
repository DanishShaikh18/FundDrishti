import { getStatusColor } from "../utils/formatters";
import "../styles/StatusBadge.css";

function StatusBadge({ status }) {
  const color = getStatusColor(status);

  return (
    <div className="status-badge" style={{ borderColor: color, color }}>
      <span className="status-dot" style={{ backgroundColor: color }}></span>
      {status}
    </div>
  );
}

export default StatusBadge;
