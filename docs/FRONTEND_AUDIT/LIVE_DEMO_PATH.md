# Live Demo Path Report

## Verified Working Live Demo Journey

```
1. Main Dashboard (Overview)
   ├── View 3D Shell-and-Tube Exchanger E-102 (Rotate / Zoom / Highlight)
   └── Inspect Real-time Process HUD (Duty Q = 4.12 MW, LMTD = 38.4 °C, U = 420 W/m²K)
        ↓
2. FOUL-X Prognosis View
   ├── Review RUL degradation curve and 30-day forecast horizon
   └── Inspect Trust Gate status (PASS)
        ↓
3. Trust Gate Reliability Stress Test Modal
   ├── Trigger +6.0 σ Out-of-Distribution (OOD) shift
   └── Verify Trust Gate transitions to ABSTAIN & activates FIXED POLICY FALLBACK
        ↓
4. Evidence Graph Modal
   ├── Click "Trace Why" to inspect H1 FOULING_ACCUMULATION hypothesis (84% confidence)
   └── Review evidence lineage and supporting/contradicting metric nodes
        ↓
5. Scenario / What-If Workbench
   ├── Adjust Hot Stream Mass Flow slider (45 → 60 kg/s)
   └── Verify delta predictions with SIMULATED badges
        ↓
6. Equipment Simulation & Thermodynamic State Inspectors
   ├── Inspect Stage 14 Mode A–D exchanger calculation card
   └── Open Chemistry Modal: Verify IDEAL_GAS, EOS UNSUPPORTED, Transport UNAVAILABLE
        ↓
7. Provenance & Benchmark Scorecards
   ├── Inspect Dataset SHA-256 Checksum (c8ed7d9c...4b4d9)
   └── Review Stage 6 Physics vs ML model accuracy benchmarks
```
