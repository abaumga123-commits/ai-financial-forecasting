# 🗺️ Project Roadmap & Work-in-Progress (WIP) Status
## AI-Driven Financial Forecasting System (Hybrid Chronos2 & Agentic Architecture)

This document outlines the current deployment status, completed milestones, and upcoming execution steps for technical reviewers. It also serves to bridge the gap between the static data layer architecture and the downstream machine learning and agentic layers.

---

## 📌 Executive Summary of Current Status
- **COMPLETED:** Core 16-file Data Generation Layer (`data_gen/`). The systemic framework for master data, costing, contracts, and general ledger architecture is fully codified and structurally verified.
- **IN PROGRESS / UP NEXT:** Building the Hybrid Time-Series Forecasting Model (TSFM) dataset, orchestrating the Agentic execution loop with GAAP/SOX Knowledge Graph guardrails, and implementing the Narrative commentary layer.

---

## 🛠️ Phase-by-Phase Roadmap

### Phase 1: Trailing 36-month Financial Statement Baseline & Few-Shot Data Staging
* **Status:** ⏳ *In Progress (Immediate Priority)*
* **Objective:** Produce 36 months of contiguous, historical training data derived from the `product.py` master files.
* **Technical Tasks:**
  - [ ] **SKU Cost Integration:** Write an aggregation script that maps unit sales price and activity-based costing (ABC) per SKU from `product.py` and `abc_costing.py` into a rolling 36-month timeline.
  - [ ] **Dual-Tier Revenue Structuring (The 80/20 Rule):** Explicitly inject a Pareto distribution into the data engine where the **Top 5 flagship products account for exactly 80%** of total revenue, and the **remaining 95 long-tail SKUs comprise 20%**.
  - [ ] **Financial Statement Generation:** Output 36 months of trailing GAAP-compliant Income Statements and Balance Sheets to serve as historical few-shot context windows for the forecasting engine.

### Phase 2: The Hybrid Time-Series Forecasting Pipeline (TSFM)
* **Status:** 🧭 *Planned (Next Milestone)*
* **Objective:** Establish a high-accuracy, resource-efficient forecasting pipeline that splits execution based on product materiality.
* **Technical Tasks:**
  - [ ] **Flagship Deep-Dive:** Pass the top 5 flagship products individually through the **Chronos2** model to output probabilistic, multi-horizon demand profiles.
  - [ ] **Long-Tail Top-Down Forecast:** Run Chronos2 at the *macro aggregate revenue level* for the remaining 20% of revenue, bypassing computationally expensive individual SKU forecasts.
  - [ ] **Pro-Rata Revenue Allocation:** Implement a standard FP&A allocation methodology (e.g., historical rolling 3-month weightings) to systematically allocate the aggregate 20% forecast back down across the remaining 95 long-tail SKUs.
  - [ ] **Financial Valuation:** Apply the static sales price and cost vectors to the forecasted units to derive projected gross profit margins.

### Phase 3: Agentic Orchestration & Economic GL Patching
* **Status:** 📋 *Planned*
* **Objective:** Build an autonomous AI agent to handle the forward-looking economic projection loop without disrupting the production month-end accounting close.
* **Technical Tasks:**
  - [ ] **Economic Forward-Close Loop:** Program the agent to operate from a purely forward-looking economic stance, acknowledging that real-world month-end close processes naturally overlap into the upcoming forecast cycle.
  - [ ] **Pro-Forma Journal Entries:** Empower the agent to automatically calculate and generate key forward-looking journal entries for:
    - **Inventory:** Expected drawdowns and replenishment cycles.
    - **Cash:** Projected collections and disbursements.
    - **Revenue & Accounts Receivable (A/R):** Invoicing lags based on contract payment terms.
    - **Accounts Payable (A/P):** Multi-entity vendor liabilities.

### Phase 4: Guardrails & "CFO-Ready" Narrative Generation
* **Status:** 📋 *Planned*
* **Objective:** Connect a semantic Knowledge Graph to a generative LLM to provide secure, auditable, and context-aware financial explanations.
* **Technical Tasks:**
  - [ ] **Knowledge Graph Enforcement:** Construct a `NetworkX` semantic graph mapping double-entry accounting constraints (e.g., $Assets = Liabilities + Equity$) to act as a hard deterministic guardrail for both the Agent and the LLM.
  - [ ] **MD&A Commentary Generation:** Fine-tune/prompt an LLM to read the Budget vs. Chronos2 Forecast variance outputs and generate professional Management Discussion & Analysis (MD&A) commentary.
  - [ ] **Governance & Controls:** Validate that the LLM's narrative output correctly captures margin drivers (e.g., pricing pressure, freight inflation) while strictly adhering to the truth boundary enforced by the Knowledge Graph.

---

## 🎯 Portfolio Presentation Highlights
1. **Financial Domain Realism:** We do not replace the historical accounting close system; we model the *forward-looking economic ledger* while managing Accounts Receivable and collection timing lags.
2. **Machine Learning Pragmatism:** The **Hybrid TSFM strategy** shows high-caliber ML engineering judgment—saving compute costs and avoiding noise by group-forecasting the long-tail 95 SKUs, while focusing model capacity on the top 5 flagship drivers.
3. **Deterministic Governance:** We mitigate LLM hallucinations completely by wrapping the reasoning layer in a **GAAP-enforcing Semantic Knowledge Graph**.