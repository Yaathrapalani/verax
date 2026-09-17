# M8.0 Command Center Specification: Industrial Process Intelligence Interface

## 1. Architecture Overview
The FOUL-X M8.0 Industrial Command Center provides the visual product layer for the validated engineering core (M2 Physics -> M3 Baselines -> M4.0 Ridge -> M5.0 Reliability Gate -> M6.0 Decision Engine -> M7.0 Policy Experiment).

```
React UI (Process View & Intelligence Panel)
   ↓
Data Adapter (`src/services/api.ts`)
   ↓
JSON Artifacts (`artifacts/m7/`, `frontend_demo_summary.json`)
   ↓
Validated Python Core (M2–M7)
```

## 2. UI Information Hierarchy & Aesthetics
- **Visual Priority**: The representative CDU process scene dominates the screen. Metrics cards and intelligence panels are secondary.
- **Visual Language**: Industrial dark graphite theme (`#071018`), restrained accents (`#27b7e8` cyan, `#34d399` green, `#f87171` red), crisp monospace typography, thin technical separators.

## 3. Representative Process Topology & Equipment Mapping
- **Disclaimer**: *REPRESENTATIVE PROCESS TOPOLOGY — NOT A PROPRIETARY PLANT BLUEPRINT*.
- **CDU Process Flow**:
  `Crude Feed -> P-101 Charge Pump -> E-101 -> E-102 (ATTN) -> E-103 -> V-101 Desalter -> E-104 -> E-105 -> V-102 Pre-Flash -> F-101 Fired Heater -> C-101 Atmospheric Distillation Column -> Product Streams`.
- **Equipment Asset ID Mapping**:
  - `E-101` -> `E01` (Heavy Naphtha Preheater)
  - `E-102` -> `E02` (Kerosene Exchanger)
  - `E-103` -> `E03` (Light Diesel Exchanger)
  - `E-104` -> `E04` (LVGO Heat Exchanger)
  - `E-105` -> `E05` (Heavy Diesel Exchanger)

## 4. Replay & Historical Navigation
- Supports deterministic replay across test period timesteps ($t = 44,800 \dots 64,000$).
- Play/Pause, Reset, and discrete timeline timestamp navigation.

## 5. FOUL-X Intelligence & Evidence Chain
- **Intelligence Panel**: Persistent copilot side-drawer displaying Current State, Derived Fouling ($R_{f,\text{derived}}$), $M4.0$ Forecast, $M5.0$ Reliability Checks (PASS/ABSTAIN), $M6.0$ Decision State, and Human Approval Invariant (`Human engineering approval required`).
- **Evidence Trace Modal**: Interactive 6-step evidence chain from Historian Measurements -> $M2$ Physics -> $R_f$ Derivation -> $M4.0$ Ridge -> $M5.0$ Reliability Gate -> $M6.0$ Decision Support.

## 6. Demo Modes & Killer Demo Flow
- **NORMAL Mode**: $M5$ Reliability Gate PASS -> $M6$ `CLEANING_REVIEW` indicated.
- **SHIFTED / STRESS TEST Mode**: Synthetic $+6.0\sigma$ regime shift applied -> $M5$ returns `REGIME_OOD` -> $M6$ returns `ABSTAIN` -> Gated policy falls back to `FIXED`.
- **Voice Adapter Boundary**: Built-in deterministic command parser supporting speech-to-text input ("Show E-102", "Why is E-102 degrading?", "Show reliability", "Show evidence", "Switch to stress test").

## 7. Operational Safety Invariant
The command center is strictly decision-support. Autonomous plant control commands, automatic valves, or automatic shutdowns are strictly forbidden.
