# PLANT-X Stage 0 — Baseline Audit

**Date:** 2026-09-17  
**Platform:** PLANT-X — Evidence-Gated Industrial Intelligence  
**Vertical:** FOUL-X — Reliability-Gated Fouling Prognosis & Maintenance Intelligence  

---

## 1. Executive Summary & Verification State

Before initiating Phase 0-14 of the PLANT-X foundation implementation, a complete repository audit was performed on the frozen FOUL-X system of record.

### Baseline Status
- **Backend Tests:** 121 / 121 PASSED (`PYTHONPATH=. uv run pytest -q`)
- **Frontend Build:** PASSED (`cd frontend && npm run build` -> `dist/assets/index-*.js`)
- **Raw Dataset Checksum (SHA-256):** `c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9`
- **Frozen Modules:** M2 Physics, M3 Forecast/Baselines, M4 Causal Ridge, M5 Reliability Gate, M6 Decision Layer, M7 Policy Experiment, M8 Dashboard, M9 Replay, M10 Deployment/API, M11 Red-Team Safety, M12 Release/Demo.

---

## 2. Directory & Module Mapping

The existing repository architecture is structured into clear engineering layers:

| Component | Path / Modules | Role & Status |
| :--- | :--- | :--- |
| **Physics State** | `src/physics/` | M2 physical fouling resistance ($R_f$), thermal effectiveness ($\epsilon$), NTU calculations. **[FROZEN]** |
| **Forecasting** | `src/forecast/`, `src/models/` | M3/M4 formulation, Causal Ridge regression, baseline models. **[FROZEN]** |
| **Reliability Gate**| `src/foulx/gate/` | M5 reliability evaluation, out-of-distribution (OOD) checks, data density gates. **[FROZEN]** |
| **Decision Layer** | `src/foulx/decision/` | M6 recommendation engine (Clean Now / Defer / Abstain), policy fallbacks. **[FROZEN]** |
| **Policy Evaluation**| `src/foulx/evaluation/` | M7 gated vs ungated policy comparison experiment logic. **[FROZEN]** |
| **Replay Engine** | `src/foulx/replay/` | M9 deterministic state replay engine indexed by historical timestamp. **[FROZEN]** |
| **Red Team** | `src/foulx/redteam/` | M11 adversarial safety test harness and stress suite. **[FROZEN]** |
| **API / Web** | `src/api/`, `frontend/` | FastAPI REST endpoints and React/Vite industrial command center dashboard. **[FROZEN]** |
| **Data Artifacts** | `data/raw/`, `artifacts/` | Dataset of record and benchmark model artifacts. **[FROZEN]** |

---

## 3. Dataset Provenance

- **Path:** `data/raw/heat_exchanger_fouling_dataset.csv`
- **SHA-256 Checksum:** `c8ed7d9c92a0c337f859bcd0374c46e8a4f431a7d37e7257d81dc38a43d4b4d9`
- **Immutability Invariant:** No modifications, row re-orderings, synthetic values, or column cleanups are permitted.

---

## 4. Proposed Integration Boundaries (PLANT-X)

To transition to PLANT-X Stage 0 without mutating FOUL-X:
1. All new canonical schemas, truth states, provenance trackers, graphs, contracts, and validators will reside strictly under `src/plantx/`.
2. Existing FOUL-X outputs (such as `ReplaySnapshot` and `CanonicalExchangerState`) will be ingested via `src/plantx/adapters/foulx_adapter.py`.
3. Mathematical calculations in M2–M11 will remain 100% untouched.

---

## 5. Frozen Invariants & Safety Declarations

- **Advisory Principle:** PLANT-X recommendations are strictly advisory and require human approval. Autonomous execution/manipulation is forbidden by safety contracts.
- **Zero Silent Inference:** Missing data or unknown geometry must never be silently imputed or converted to observed parameters.
