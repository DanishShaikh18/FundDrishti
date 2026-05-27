import React from "react";
import { formatTimestamp, formatCurrency } from "../utils/formatters";
import "../styles/Timeline.css";

function Timeline({ edges }) {
  if (!edges || edges.length === 0) {
    return (
      <div className="timeline-empty">
        <p>No transaction history to display on timeline.</p>
      </div>
    );
  }

  // Sort transactions chronologically
  const sortedTransactions = [...edges].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  );

  return (
    <div className="timeline-container">
      <div className="timeline-list">
        {sortedTransactions.map((tx, index) => {
          const isLarge = tx.amount > 100000;
          return (
            <div key={index} className={`timeline-item ${isLarge ? "suspicious-tx" : ""}`}>
              <div className="timeline-marker">
                <div className="timeline-dot"></div>
                {index < sortedTransactions.length - 1 && <div className="timeline-line"></div>}
              </div>
              <div className="timeline-content">
                <div className="timeline-time">
                  {formatTimestamp(tx.timestamp)}
                </div>
                <div className="timeline-tx-details">
                  <span className="account-pill from-acc">{tx.source}</span>
                  <span className="tx-arrow">→</span>
                  <span className="account-pill to-acc">{tx.target}</span>
                </div>
                <div className="timeline-meta">
                  <div className="tx-amount">
                    {formatCurrency(tx.amount)}
                  </div>
                  <div className="tx-channel-badge">{tx.channel || "TRANSFER"}</div>
                </div>
                {tx.narration && (
                  <p className="tx-narration">"{tx.narration}"</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Timeline;
