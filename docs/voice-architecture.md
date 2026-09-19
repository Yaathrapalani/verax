# PLANT-X / FOUL-X Voice System Architecture

## 1. System Overview

The PLANT-X voice interface serves as an operator control and query plane for the industrial engineering workstation. It operates across all views—Process Topology, P&ID Schematic, 3D Representative Spatial Layout, Trends/Fouling Analysis, Scenario Simulation, Evidence Lineage Graph, and Chemical Stream Builder.

```
USER
  │ (Audio / Ctrl+K)
  ▼
WorkstationShell (Persistent Shell)
  │
  ├── VoiceAssistantController (Workstation-Wide Singleton)
  │     ├── RealtimeAudioController (Microphone, Web Audio API, VAD, Barge-In)
  │     ├── VoiceProviderRegistry (Gemini Live, Browser Speech, Text Only, Demo)
  │     ├── IntentParser (Grammar, Pronoun Resolution, Context Tracking)
  │     ├── ConversationContext (Multi-Turn Epistemic History)
  │     ├── TruthFirewall (Enforces Epistemic Integrity & Claim Safety)
  │     ├── ToolRegistry (Deterministic Engineering Tools)
  │     ├── TimerService (Pre-validated Countdown & Cancellation)
  │     └── AuditLogger (Immutable Chronological Action Log)
  │
  ├── Authoritative Plant State (Canonical Single Source of Truth)
  │     ├── activeView
  │     ├── selectedAssetTag
  │     ├── selectedStreamId
  │     ├── highlightedPath
  │     ├── cameraFocusTag
  │     ├── scenario / study
  │     └── trustGateStatus / currentRf
  │
  └── Visual Projections (Derive deterministically from State)
        ├── 2D P&ID SVG View
        ├── 3D WebGL Scene Graph (Three.js / React Three Fiber)
        ├── Dynamic Inspector & Parameter Sheet
        └── Causal Evidence Lineage
```

## 2. Core Architectural Principles

1. **Voice is an Interface, Not the Source of Truth**: The voice layer never directly mutates or calculates plant truth. It resolves operator intent into typed, validated tool invocations.
2. **Epistemic Integrity via Truth Firewall**:
   - `OBSERVED`: Grounded in immutable plant telemetry (sensor readings, timestamps).
   - `DERIVED`: Deterministically calculated via frozen thermodynamic equations ($Q = U A \Delta T_{lm}$, $R_f = 1/U - 1/U_0$).
   - `INFERRED`: Machine learning outputs (FOUL-X temporal model predictions).
   - `SIMULATED`: Generated via the Stage 9/14 counterfactual equipment runtime.
   - `REPRESENTATIVE`: Visual geometry compiled procedurally (Level L4); distinguished from genuine CAD (Level L5).
   - `UNAVAILABLE`: Gaps in data (e.g., differential pressure $\Delta P$, transport properties like viscosity).
3. **Persistent Workstation Presence**:
   - The assistant controller is a singleton (`VoiceAssistantController.getInstance()`) registered above individual view routes.
   - Navigating between views does not destroy conversational turns, entity memory, or running timers.
4. **Natural Follow-Up & Contextual Continuity**:
   - Operator queries such as "Why?", "What's missing?", "What should I investigate next?", "Compare with baseline", and "What am I looking at?" resolve deterministically against active state.
5. **Barge-In and Cancellation Safety**:
   - Operator speech detection immediately halts TTS audio playback via `stopSpeaking()`.
   - Action cancellation ("Cancel") explicitly disarms pending timers and delayed simulations without race conditions.
