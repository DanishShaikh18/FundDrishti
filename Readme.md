# FundDrishti

**Agentic Financial Crime Investigation Platform**

FundDrishti is a graph-based AML intelligence system that transforms suspicious transaction alerts into complete, investigator-ready case files in under 3 minutes. It combines multi-agent reasoning, graph analytics, and explainable ML to solve the last-mile problem in anti-money laundering — the gap between detection and actionable intelligence.

---

## The Problem

Enterprise AML systems (Actimize, SAS, Oracle FCCM) generate thousands of alerts daily with a 95–99% false positive rate. When a real alert fires, investigators spend 3–7 days manually logging into 8 separate systems, building transaction graphs by hand, and writing FIU narratives from scratch.

The bottleneck is not detection. It is that detected signals never become actionable intelligence efficiently.

---

## What FundDrishti Does

FundDrishti is not another detector. It is the force multiplier on top of existing detectors — an autonomous investigation agent that does what a senior AML investigator does, in 3 minutes instead of 3 days.

When an alert fires, the system:

1. Identifies the fraud pattern type from five detection engines
2. Adaptively scopes three specialized agents to the relevant subgraph only
3. Fuses agent findings into a point-traceable risk score with data-derived weights
4. Drafts a structured FIU investigation narrative via Gemini API
5. Generates a downloadable evidence package — PDF report and goAML-compliant XML

The investigator reviews, signs, and submits. Their review time: under 20 minutes instead of 3 days.

---

## Five Fraud Patterns Detected

| Pattern | Algorithm | Novel Aspect |
|---|---|---|
| Structuring / Smurfing | Fan-in detection + amount clustering | Channel-aware RBI threshold enforcement |
| Layering | BFS traversal + temporal sequence validation | Timestamp ordering validation — B→C must follow A→B |
| Round-trip / Circular | DFS cycle detection + time + amount constraints | 72-hour window + 15% amount tolerance |
| Coordinated dormant activation | Temporal subgraph + Louvain community detection | Reactivation events modelled as a graph — novel representation |
| Profile mismatch | Z-score anomaly within declared peer group | Compared against profile category benchmark, not global population |

---

## Architecture
Transaction DB → Pattern Detectors (5)
↓
Adaptive Orchestrator (LangGraph)
reads pattern type → scopes agents to relevant subgraph only
↓
┌───────────────┼───────────────┐
Graph Agent    Profile Agent   Temporal Agent
NetworkX       Z-score         Sequence + dormancy
└───────────────┼───────────────┘
↓
Fusion Layer
LR-derived weights · point-traceable score
↓
FIU Evidence Package
Gemini narrative · ReportLab PDF · goAML XML
Human sign-off required before submission

**What makes the orchestrator genuinely agentic:** it does not run all agents on all accounts. It reads the detected pattern type and dynamically scopes which agents run on which subgraph. A hub pattern scopes the Profile Agent to 2nd-degree neighbors only. A dormant activation pattern runs the Temporal Agent bank-wide in cluster mode. The next action is determined by the prior finding — that is the definition of agentic.

---

## Explainable Scoring

Every risk score point traces to a specific finding. Score weights are not arbitrary — they are derived from Logistic Regression coefficients trained on 1000 labeled synthetic cases.
Risk Score: 87/100

35 pts  Structuring detected         LR coefficient — highest discriminative pattern
25 pts  Temporal velocity burst      Temporal Agent finding
15 pts  Watchlist proximity          Direct hit on RBI pre-seeded watchlist
12 pts  Hub detected (in-degree 4)  Graph Agent finding


When a regulator asks "why 35 points for structuring?" — the answer is: because the logistic regression coefficient for structuring_detected was the highest of all five features in the labeled dataset. The weights are learned, not chosen.

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Graph engine | NetworkX | Every algorithm is readable Python — fully auditable |
| Agent orchestration | LangGraph | State persistence, retry handling, adaptive routing |
| ML — scoring | scikit-learn Logistic Regression | Coefficients become score weights — data-derived and defensible |
| ML — profile anomaly | Z-score within peer group | Transparent, explainable in 20 seconds, stable at demo scale |
| LLM — narrative | Google Gemini API | Grounded on structured findings — no hallucination risk |
| Backend | FastAPI | Async, clean, auto-docs |
| Database | SQLite | Zero-setup, sufficient for current scale |
| Frontend | React + Cytoscape.js + Recharts | Interactive graph viz + behavioral radar |
| FIU Report | ReportLab PDF + Python XML | goAML ARF schema — ARFBAT, ARFRPT, ARFACC, ARFTRN, ARFINP |
| Deployment | Render | Zero-config deploy from GitHub |

---

## Running Locally

```bash
# 1. Clone
git clone https://github.com/your-username/funddrishti.git
cd funddrishti/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create database and generate synthetic data
python database.py
python synthetic/generator.py

# 4. Start backend
uvicorn main:app --reload
# API docs at http://localhost:8000/docs

# 5. Start frontend
cd ../frontend
npm install
npm run dev
```

Add a `.env` file in the backend folder:
GEMINI_API_KEY=your_key_here

Narrative generation falls back to a structured template if the key is absent — the system works without it.

---

## Evaluation

Evaluated on 1000 synthetic labeled cases across five pattern types, including 300 clean-but-suspicious cases (NRI remittances, bulk payroll, seasonal agricultural, chit fund collections) as false positive stress tests.

| Pattern | Precision | Recall | F1 |
|---|---|---|---|
| Structuring | — | — | — |
| Layering | — | — | — |
| Round-trip | — | — | — |
| Dormant activation | — | — | — |
| Profile mismatch | — | — | — |

*Run `python backend/evaluate.py` to generate confusion matrix on your local data.*

---

## Production Path

FundDrishti is deliberately built for transparency at current scale. The production migration path is a data-layer swap, not an architectural change.

| Component | Current | Production |
|---|---|---|
| Graph engine | NetworkX (in-memory) | Neo4j AuraDB / TigerGraph |
| Database | SQLite | TimescaleDB |
| Processing | Single process | Celery + Redis worker pool |
| Streaming | Batch | Apache Kafka → Flink |
| ML lifecycle | Manual | MLflow + automated retraining |
| Deployment | Render | Kubernetes cluster |

---

## Known Limitations

- NetworkX does not scale beyond demo-size transaction volumes — Neo4j is the documented production path
- All transaction data is synthetic — real deployment requires core banking integration
- goAML XML implements STR core fields — full schema is extensible per FIU-IND requirements
- Narrative generation requires Gemini API key — template fallback is available

---

## Author

**Danish Shaikh**  
[GitHub](https://github.com/DanishShaikh18) · [LinkedIn](https://www.linkedin.com/in/danish-shaikh-b6442a212/)