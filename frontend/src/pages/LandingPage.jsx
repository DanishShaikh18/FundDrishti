import { useEffect } from "react";
import { Link } from "react-router-dom";
import "../styles/LandingPage.css";

function LandingPage() {
  useEffect(() => {
    // Select all elements with the 'reveal' class
    const revealElements = document.querySelectorAll(".reveal");

    // Fallback if IntersectionObserver is not supported
    if (!("IntersectionObserver" in window)) {
      revealElements.forEach((el) => el.classList.add("active"));
      return;
    }

    // IntersectionObserver Options
    const observerOptions = {
      root: null,
      rootMargin: "0px 0px -80px 0px",
      threshold: 0.12,
    };

    // IntersectionObserver Callback
    const observer = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("active");
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    revealElements.forEach((el) => observer.observe(el));

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <div className="landing-page-wrapper">
      {/* Background Animated Gradient Orbs */}
      <div className="bg-orbs-container" aria-hidden="true">
        <div class="orb orb-purple"></div>
        <div class="orb orb-cyan"></div>
        <div class="orb orb-pink"></div>
      </div>

      {/* Navigation Bar (Glassmorphic) */}
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-logo" id="nav-logo">
            <svg className="logo-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="url(#logo-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="url(#logo-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="url(#logo-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="logo-grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#c084fc" />
                  <stop offset="1" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>
            <span>FundDrishti</span>
          </Link>
          <ul className="nav-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#about">Technology</a></li>
            <li><a href="#demo" className="nav-btn-link">Request Demo</a></li>
          </ul>
          <Link to="/dashboard" className="nav-cta-btn" id="nav-cta-console">Launch Console</Link>
        </div>
      </nav>

      {/* Main Content Wrapper */}
      <main>
        {/* Hero Section */}
        <section className="hero-section" id="hero">
          <div className="hero-content">
            <div className="badge reveal">
              <span className="badge-dot"></span>
              <span className="badge-text">Next-Gen Fraud Investigation Console</span>
            </div>
            
            <h1 className="hero-title reveal">
              Unveil Hidden <span className="gradient-text">Financial Risks</span> in Real-Time
            </h1>
            
            <p className="hero-subtitle reveal">
              Trace complex fund flows, isolate fraud clusters, and audit transactions with interactive graph intelligence and predictive agentic models.
            </p>
            
            <div className="hero-actions reveal">
              <Link to="/dashboard" className="btn-solid" id="hero-btn-start">
                <span>Start Investigating</span>
                <svg className="btn-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </Link>
              <a href="#demo" className="btn-glass" id="hero-btn-demo">
                <span>Watch Demo</span>
              </a>
            </div>
          </div>
          
          <div className="hero-scroll-indicator reveal">
            <span className="scroll-text">Explore Features</span>
            <div className="scroll-mouse">
              <div className="scroll-wheel"></div>
            </div>
          </div>
        </section>

        {/* Feature Grid Section */}
        <section className="features-section" id="features">
          <div className="section-header">
            <span className="section-tag reveal">Capabilities</span>
            <h2 className="section-title reveal">Built for Deep Forensic Audits</h2>
            <p className="section-subtitle reveal">
              Equipped with powerful components designed to map, evaluate, and mitigate financial vulnerabilities.
            </p>
          </div>

          <div className="feature-grid">
            
            {/* Feature Card 1 */}
            <div className="glass-card feature-card reveal" style={{ transitionDelay: "0ms" }}>
              <div className="card-icon-wrapper purple-glow">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="18" cy="18" r="3"></circle>
                  <circle cx="6" cy="6" r="3"></circle>
                  <circle cx="18" cy="6" r="3"></circle>
                  <circle cx="6" cy="18" r="3"></circle>
                  <line x1="18" y1="9" x2="18" y2="15"></line>
                  <line x1="9" y1="6" x2="15" y2="6"></line>
                  <line x1="8.12" y1="8.12" x2="15.88" y2="15.88"></line>
                </svg>
              </div>
              <h3 className="card-title">Interactive Graph Intelligence</h3>
              <p className="card-description">
                Visualize intricate transaction networks and trace fund velocity across infinite hops. Isolate cyclic flows, coinjoin mixers, and suspicious shell clusters instantly.
              </p>
              <a href="#graph" className="card-link" id="feature-link-graph">
                <span>Learn more</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </a>
            </div>

            {/* Feature Card 2 */}
            <div className="glass-card feature-card reveal" style={{ transitionDelay: "120ms" }}>
              <div className="card-icon-wrapper cyan-glow">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  <circle cx="12" cy="11" r="3"></circle>
                  <path d="M9 17v-1.5a3 3 0 0 1 6 0V17"></path>
                </svg>
              </div>
              <h3 className="card-title">Predictive Risk Scoring</h3>
              <p className="card-description">
                Evaluate transfers with dynamic machine learning heuristics. Rank wallets by fraud probability, flag structural velocity patterns, and configure triggers for compliance.
              </p>
              <a href="#risk" className="card-link" id="feature-link-risk">
                <span>Learn more</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </a>
            </div>

            {/* Feature Card 3 */}
            <div className="glass-card feature-card reveal" style={{ transitionDelay: "240ms" }}>
              <div className="card-icon-wrapper pink-glow">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
              </div>
              <h3 className="card-title">Autonomous Audit Agents</h3>
              <p className="card-description">
                Deploy background AI checkers that constantly verify records, audit ledger compliance, and output human-readable case reports with visual ledger state summaries.
              </p>
              <a href="#agents" class="card-link" id="feature-link-agents">
                <span>Learn more</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </a>
            </div>

          </div>
        </section>
      </main>

      {/* Footer (Glassmorphic) */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-brand">
            <span>FundDrishti</span>
            <p className="footer-copy">&copy; 2026 FundDrishti. All rights reserved.</p>
          </div>
          <div className="footer-links">
            <a href="#privacy">Privacy</a>
            <a href="#terms">Terms</a>
            <a href="https://github.com/DanishShaikh18/FundDrishti" target="_blank" rel="noopener noreferrer" className="github-link" id="footer-github-link">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
              </svg>
              <span>GitHub</span>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
