/**
 * API Configuration
 */
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  TIMEOUT: 30000,
};

/**
 * UI Constants
 */
export const UI_CONSTANTS = {
  COLORS: {
    DARK_BG: "#0f172a",
    LIGHT_BG: "#1e293b",
    BORDER: "#334155",
    TEXT_PRIMARY: "#e2e8f0",
    TEXT_SECONDARY: "#94a3b8",
    ACCENT: "#3b82f6",
  },
  STATUS: {
    OPEN: "Open",
    INVESTIGATING: "Investigating",
    CLOSED: "Closed",
  },
  PATTERN_TYPES: [
    "Structuring",
    "Layering Chain",
    "Round-Trip",
    "Coordinated Dormancy",
    "Profile Mismatch",
  ],
};

/**
 * Radar Chart Axes
 */
export const RADAR_AXES = [
  "account_age_days",
  "avg_transaction_size",
  "transaction_frequency",
  "dormancy_days",
  "geographic_variance",
  "network_centrality",
  "risk_indicator",
];

/**
 * Cytoscape Graph Configuration
 */
export const CYTOSCAPE_CONFIG = {
  style: [
    {
      selector: "node",
      style: {
        "background-color": "#3b82f6",
        label: "data(label)",
        "text-valign": "bottom",
        "text-halign": "center",
        "text-margin-y": 6,
        color: "#ffffff",
        width: 34,
        height: 34,
        "font-size": 11,
        "font-weight": "bold",
        "font-family": "Outfit, Inter, sans-serif",
      },
    },
    {
      selector: 'node[role="victim"]',
      style: {
        "background-color": "#06b6d4",
      },
    },
    {
      selector: 'node[role="suspect"]',
      style: {
        "background-color": "#f472b6",
      },
    },
    {
      selector: 'node[role="intermediary"]',
      style: {
        "background-color": "#c084fc",
      },
    },
    {
      selector: "edge",
      style: {
        "line-color": "rgba(255, 255, 255, 0.15)",
        "target-arrow-color": "rgba(255, 255, 255, 0.15)",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        label: "data(label)",
        "font-size": 9,
        color: "rgba(255, 255, 255, 0.8)",
        "text-background-opacity": 0.85,
        "text-background-color": "#070310",
        "text-background-padding": 4,
        "text-background-shape": "roundrectangle",
        width: 2,
      },
    },
  ],
  layout: {
    name: "cose",
    animate: true,
    animationDuration: 500,
  },
};
