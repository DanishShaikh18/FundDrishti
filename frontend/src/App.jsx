import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AppProvider } from "./context/AppContext";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import CaseDetail from "./pages/CaseDetail";
import "./styles/App.css";

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="app-container">
          {/* Persistent Background Animated Orbs */}
          <div className="bg-orbs-container" aria-hidden="true">
            <div className="orb orb-purple"></div>
            <div className="orb orb-cyan"></div>
            <div className="orb orb-pink"></div>
          </div>

          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/case/:caseId" element={<CaseDetail />} />
          </Routes>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
