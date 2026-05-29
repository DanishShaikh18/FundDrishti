import { BrowserRouter, Routes, Route } from "react-router-dom";
import AlertQueue from "./pages/AlertQueue";
import Investigation from "./pages/Investigation";
import CaseReview from "./pages/CaseReview";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ fontFamily: "Inter, sans-serif", background: "#0f1117", minHeight: "100vh", color: "#e2e8f0" }}>
        <nav style={{ padding: "14px 28px", borderBottom: "1px solid #1e2530", display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontWeight: 700, fontSize: "18px", color: "#60a5fa" }}>FundDrishti</span>
          <span style={{ fontSize: "12px", color: "#64748b", marginLeft: "4px" }}>AML Investigation Console</span>
        </nav>
        <Routes>
          <Route path="/" element={<AlertQueue />} />
          <Route path="/investigate/:patternType/:accounts" element={<Investigation />} />
          <Route path="/case/:caseId" element={<CaseReview />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}