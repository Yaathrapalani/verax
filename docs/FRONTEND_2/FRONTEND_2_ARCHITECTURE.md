# PLANT-X Frontend 2.0 — Architecture & Rebuild Plan

## Executive Overview
PLANT-X Frontend 2.0 transitions the UI from an AI-centric dashboard to a serious **Industrial Engineering Workstation**. The computational plant is the primary authority around which all visual elements, views, and inspector tools pivot.

## Key Architectural Principles
1. **Plant-Centric State Model (`PlantClientState`)**:
   - Single canonical frontend state tree.
   - 3D Viewport, Process PFD, Trends, Simulation, and Evidence views are non-destructive projections of `PlantClientState`.
   - Selected object (`selectedAssetTag`) persists seamlessly across view switching.
2. **Industrial Design System**:
   - Restrained industrial palette (Dark slate `#090d16`, neutral borders `#1e293b`, clear status tokens).
   - Zero neon glow, zero glassmorphism cards, zero AI dashboard aesthetics.
   - Precise tabular typography (`font-mono` for metrics, aligned units and exponents).
3. **Application Shell Architecture**:
   - **Top Application Bar**: Workstation title, Plant Selector (`Crude Preheat Train 1`), Study Selector (`Base Case`), Simulation/Replay state, Time clock.
   - **Left Plant Explorer**: Hierarchical tree (Plant → Process Units E-101..E-105 → Streams S-101..S-106 → Instruments TT/PT/FT).
   - **Center Workspace**: View Mode Switcher (`PROCESS`, `P&ID`, `3D`, `TRENDS`, `SIMULATION`, `EVIDENCE`).
   - **Right Inspector**: Tabbed Engineering Inspector (`Identity`, `State`, `Measurements`, `Thermodynamics`, `Performance`, `Fouling`, `Simulation`, `Evidence`, `Provenance`).
   - **Bottom Status Bar**: Solver status, Data State (`OBSERVED`), Validation (`VALID`), Trust Gate (`PASS`/`ABSTAIN`), Units (`SI`), Dataset SHA-256.
   - **Contextual Copilot**: Non-intrusive command bar / collapsible side panel.
