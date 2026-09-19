# Frontend Migration Plan

## Phase 1: Core Shell & Design System
- Replace top banner / header with Workstation Shell (`TopBar`, `PlantExplorer`, `Inspector`, `StatusBar`).
- Migrate CSS to industrial color palette (`#090d16` slate theme).

## Phase 2: View Switcher & Universal Inspector
- Refactor `PlantScene3D` and `PlantProcessOverlay` into unified `PlantWorkspace`.
- Implement selection state persistence across `PROCESS`, `P&ID`, `3D`, `TRENDS`, `SIMULATION`, `EVIDENCE` views.
- Implement right-side tabbed `EngineeringInspector`.

## Phase 3: Copilot & Modal Contextualization
- Move persistent copilot side panel into collapsible contextual drawer and command palette (`Ctrl+K`).
- Ensure all judging modals (`TrustGateModal`, `EvidenceOverlay`, `ChemistryModal`) use industrial workstation design system.
