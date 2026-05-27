/**
 * Format timestamp to human-readable format
 */
export const formatTimestamp = (timestamp) => {
  try {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(date);
  } catch (error) {
    return timestamp;
  }
};

/**
 * Format currency amount
 */
export const formatCurrency = (amount) => {
  if (typeof amount !== "number") return "$0.00";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format large numbers with K, M, B notation
 */
export const formatNumber = (num) => {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1) + "B";
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toString();
};

/**
 * Get status badge color
 */
export const getStatusColor = (status) => {
  const statusColors = {
    Open: "#ef4444",
    Investigating: "#f59e0b",
    Closed: "#10b981",
  };
  return statusColors[status] || "#6b7280";
};

/**
 * Get pattern type icon/label
 */
export const getPatternLabel = (patternType) => {
  const labels = {
    Structuring: "📊",
    "Layering Chain": "⛓️",
    "Round-Trip": "🔄",
    "Coordinated Dormancy": "😴",
    "Profile Mismatch": "⚠️",
  };
  return labels[patternType] || "❓";
};
