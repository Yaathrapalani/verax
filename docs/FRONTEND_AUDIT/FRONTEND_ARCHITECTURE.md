# PLANT-X Frontend Architecture Audit (Stages 0–14)

## Overview
The PLANT-X frontend is a single-page, high-density industrial digital shadow application built using React 19, TypeScript, Vite, TailwindCSS v4, Three.js (React Three Fiber / `@react-three/drei`), Lucide Icons, and Canvas-based charts.

## Project Structure
- **Frontend Root**: `frontend/`
- **Framework**: React 19.0.0
- **Build Tool / Bundler**: Vite 6.2.0
- **Language**: TypeScript 5.7.3
- **Package Manager**: npm (`package.json`, `package-lock.json`)
- **Styling System**: TailwindCSS v4 (`@tailwindcss/vite`) + Custom Glassmorphism CSS in `src/index.css`
- **3D Graphics Engine**: Three.js 0.174.0, `@react-three/fiber` 9.1.0, `@react-three/drei` 10.0.4
- **Icons**: `lucide-react` 0.475.0
- **Animation**: Lucide Icons, CSS transitions, RequestAnimationFrame canvas loops
- **Routing Engine**: State-driven SPA view state (`App.tsx` tab/view router) with explicit modals and drawers.

## Core Modules & Components Directory Structure
```
frontend/src/
├── App.tsx                     # Main App View Router, State Orchestrator, & Layout
├── main.tsx                    # React Root Entrypoint
├── index.css                   # Glassmorphism design system, CSS custom variables
├── components/
│   ├── PlantScene3D.tsx        # WebGL 3D Interactive Plant Model (Three.js/Canvas)
│   ├── PlantProcessOverlay.tsx # Real-time Process HUD (Mass/Energy flow, FOUL-X cards)
│   ├── FoulXCopilot.tsx        # AI Assistant / Evidence Graph / Trust Gate Drawer
│   ├── EvidenceOverlay.tsx     # Full Evidence Chain Modal & Hypotheses Visualizer
│   ├── TrustGateModal.tsx      # Reliability Gate & +6σ Stress Test Controller
│   ├── IndustrialIntakeModal.tsx# Evidence Intake & Document Verification UI
│   ├── BlueprintModal.tsx      # Process Flow Diagram (PFD) / Topology View
│   ├── ProvenanceModal.tsx     # Cryptographic Provenance Ledger & SHA-256 Hashes
│   ├── BenchmarkModal.tsx      # Model Benchmark Scorecard & Model Comparison
│   └── ChemistryModal.tsx      # Fluid Chemistry & EOS Property Package Inspector
├── data/
│   └── mockData.ts             # Client-side heat exchanger telemetry, models, & forecasts
└── types/
    └── index.ts                # TypeScript domain models (Telemetry, Evidence, Hypotheses)
```
