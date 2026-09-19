# PLANT-X Screen Inventory Audit

| SCREEN / OVERLAY NAME | TYPE | CLASSIFICATION | DESCRIPTION |
|---|---|---|---|
| Main Dashboard (Overview) | Dashboard Page | `PARTIAL` | 3D WebGL plant canvas + top metrics bar (0.00042 m²K/W fouling, PASS trust gate) |
| Process HUD Overlay | Floating Overlay | `PARTIAL` | Live stream telemetry cards, Q/LMTD/UA indicators, active alarm badges |
| Digital Shadow 3D Viewport | 3D Canvas | `PARTIAL` | Interactive 3D shell-and-tube exchanger model with rotation, zoom, and highlight controls |
| FOUL-X Prognosis Panel | Tab View | `PARTIAL` | RUL forecast plot, fouling growth curve, cleaning window recommendation |
| Trust Gate Stress Test Modal | Modal Overlay | `PARTIAL` | Selective prediction toggle (+6σ OOD trigger), calibration error indicator |
| Evidence Graph Modal | Modal Overlay | `PARTIAL` | H1–H5 hypothesis matrix, supporting/contradicting evidence chain |
| Scenario / What-If Workbench | Tab View | `PARTIAL` | Interactive parameter adjustment (inlet temp, flow rate) with delta predictions |
| Decision Intelligence Drawer | Side Drawer | `PARTIAL` | Action recommendations (CONTINUE vs CLEANING_REVIEW) with human approval barrier |
| Process Blueprint (PFD) Modal | Modal Overlay | `UI_ONLY` | Visual PFD topology diagram showing E-101, E-102, P-101 connectivity |
| Industrial Intake Modal | Modal Overlay | `UI_ONLY` | File drag-and-drop intake zone with SHA-256 validation simulation |
| Provenance & Lineage Modal | Modal Overlay | `UI_ONLY` | Immutable ledger view showing SHA-256 data hashes and verification status |
| Model Benchmark Scorecard Modal | Modal Overlay | `UI_ONLY` | Stage 6 physics vs ML baseline accuracy comparison metrics |
| Thermodynamic State Inspector Modal | Modal Overlay | `UI_ONLY` | Property package selection (IDEAL_GAS), EOS availability, vapor/gas phase specs |
