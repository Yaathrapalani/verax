# PLANT-X Route Inventory Audit

| ROUTE / VIEW STATE | PAGE / COMPONENT | PURPOSE | STATUS | BACKEND CONNECTED? | DATA SOURCE | AUTH REQUIRED? | ERROR HANDLING | RESPONSIVE? | NOTES |
|---|---|---|---|---|---|---|---|---|---|
| `/` (Tab: `overview`) | `PlantScene3D` + `PlantProcessOverlay` | Live 3D Plant Shadow & Real-time Process HUD | `PARTIAL` | `UI_ONLY` | `mockData.ts` (Client state) | No | Graceful Fallback | Yes (Collapsible HUD) | Renders 3D exchanger E-102 and process streams |
| `/` (Tab: `foulx`) | `PlantProcessOverlay` (FOUL-X mode) | FOUL-X Prognosis & Trust Gate View | `PARTIAL` | `UI_ONLY` | `mockData.ts` | No | Component Error Boundary | Yes | Highlights E-102 fouling state (0.00042 m²K/W) |
| `/` (Tab: `evidence`) | `EvidenceOverlay` | Evidence Graph & Diagnostic Hypotheses | `PARTIAL` | `UI_ONLY` | `mockData.ts` | No | Render check | Yes | Displays H1-H5 evidence matrix and trace paths |
| `/` (Tab: `simulations`) | `PlantProcessOverlay` (What-If mode) | Scenario / Counterfactual Simulator | `PARTIAL` | `UI_ONLY` | Client calc | No | Form validation | Yes | Allows adjusting flow/temp sliders for E-102 |
| `/` (Tab: `pfd`) | `BlueprintModal` | Computational Plant Graph PFD | `UI_ONLY` | No | Static SVG / CSS | No | None | Yes | Displays stream connectivity and node specs |
| `/` (Tab: `copilot`) | `FoulXCopilot` | Decision Support Copilot Drawer | `PARTIAL` | `UI_ONLY` | `mockData.ts` | No | Inline alerts | Yes | Provides cleaning window recommendation & gate status |
| `/` (Modal: `trust_gate`) | `TrustGateModal` | Reliability Gate & Stress Test | `PARTIAL` | `UI_ONLY` | `mockData.ts` | No | Fail-safe UI state | Yes | Interactive +6σ OOD stress test trigger |
| `/` (Modal: `intake`) | `IndustrialIntakeModal` | Stage 1 Evidence Intake | `UI_ONLY` | No | Local state | No | Upload validation | Yes | Allows drag-and-drop document intake simulation |
| `/` (Modal: `provenance`) | `ProvenanceModal` | Cryptographic SHA-256 Lineage | `UI_ONLY` | No | `mockData.ts` | No | None | Yes | Shows dataset SHA-256 checksums |
| `/` (Modal: `benchmarks`) | `BenchmarkModal` | Stage 6 Model Benchmarks | `UI_ONLY` | No | `mockData.ts` | No | None | Yes | Displays RMSE/MAE benchmark scorecard |
| `/` (Modal: `chemistry`) | `ChemistryModal` | Stage 13 Thermodynamic State Inspector | `UI_ONLY` | No | `mockData.ts` | No | None | Yes | Displays IDEAL_GAS EOS property package specs |
