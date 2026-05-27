import { Link } from "react-router-dom";
import AlertDashboard from "../components/AlertDashboard";
import "../styles/Dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard-page">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left-brand">
            <Link to="/" className="nav-logo" style={{ textDecoration: "none", color: "inherit", display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <svg className="logo-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ filter: "drop-shadow(0 0 8px rgba(192, 132, 252, 0.5))" }}>
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logo-grad-dash)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="url(#logo-grad-dash)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L17L22 12" stroke="url(#logo-grad-dash)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                <defs>
                  <linearGradient id="logo-grad-dash" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#c084fc" />
                    <stop offset="1" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>
              </svg>
              <h1 style={{ margin: 0, fontSize: "1.4rem", fontFamily: "var(--font-display)", fontWeight: 700, letterSpacing: "-0.5px" }}>FundDrishti</h1>
            </Link>
            <p className="subtitle" style={{ marginTop: "0.25rem" }}>
              Real-time fraud pattern detection & investigation console
            </p>
          </div>
          <div className="header-right-actions">
            <Link to="/" className="back-button" style={{ textDecoration: "none" }}>
              ← Return Home
            </Link>
          </div>
        </div>
      </header>
      <main className="dashboard-main">
        <AlertDashboard />
      </main>
    </div>
  );
}

export default Dashboard;
