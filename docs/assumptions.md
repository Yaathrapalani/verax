# Assumptions Register

| ID | Assumption | Status | Validation needed |
|---|---|---|---|
| A-001 | Prototype may use public/synthetic historian-like data | Working assumption | Document dataset provenance |
| A-002 | Cleaning events can be represented as explicit cycle boundaries when available | Working assumption | Validate against dataset |
| A-003 | Recommendations are advisory and require human approval | Product requirement | Confirm with industrial reviewer |
| A-004 | A fixed maintenance policy can be represented for comparative evaluation | Experimental assumption | Define policy from evidence/dataset |
| A-005 | Economic quantities are only reported when source data or explicit assumptions support them | Non-negotiable | Document all values |
| A-006 | Web Speech API is utilized for voice STT/TTS with keyboard/text input parity; offline fallback deterministic | Working assumption | Ensure full accessible keyboard navigation |
| A-007 | Agent intent resolution maps to deterministic tool registry; no direct state or calculation bypass | Non-negotiable | Enforce typed tool boundaries |
| A-008 | 3D process topology is synthetic and illustrative; clearly tagged as non-validated CAD | Working assumption | Display visible disclaimer badge |
| A-009 | Scheduled actions revalidate project state at execution time; abort if state mutated during countdown | Safety requirement | Covered by regression tests |
| A-010 | Hypotheses (H1-H5) are evidence-grounded decision support; causality is never claimed without evidence | Scientific honesty | Counter-evidence and next test required |
| A-011 | Voice architecture uses Gemini 3.8 Live with ephemeral server credentials; falls back to Web Speech / text without fake states | Security requirement | Never expose server API key to browser |
| A-012 | Truth Firewall prevents truth state escalation (INFERRED/SIMULATED to OBSERVED); transport properties remain UNAVAILABLE | Scientific honesty | Audited by regression tests |
| A-013 | Spatial solver computes procedural coordinates from graph topology heuristics; not proprietary plant CAD | Working assumption | Display visible L2 disclaimer |
| A-014 | Human-in-the-loop P&ID review audits connection confirmations into immutable event log | Traceability | Logged in graph audit trail |
| A-015 | Multi-step command plans execute asynchronously with state versioning; abort on concurrent state collision | Concurrency safety | State version checked on each step |
| A-016 | Realtime audio layer uses browser-native Web Audio and RMS VAD; barge-in cancels speech while preserving task lifecycle | Performance/UX | Audited by audio unit tests |
| A-017 | Voice reconnection restores workstation state and revalidates pending operations; rejects stale results | Reliability | Verified by resume controller tests |
| A-018 | External MCP servers are strictly untrusted; physical DCS/PLC valve/setpoint controls are hard-prohibited | Industrial Safety | Enforced by MCPGateway policy |
| A-019 | Geometry pipeline strictly separates Path A (L0-L4 inferred representative) from Path B (L5 source CAD/IFC) | Scientific honesty | Verified by GeometryService tests |
| A-020 | 3D scene replacement uses versioned candidates; hot-swap activation maintains history and supports instant rollback | System Integrity | Verified by SceneVersionManager tests |
| A-021 | Face-presence voice activation is presence-detection only; strictly browser-local, zero face recognition, zero embeddings, zero cloud uploads | Privacy & Safety | Enforced by FacePresenceDetector and default OFF mode |
| A-022 | Judge Walkthrough executes 19 deterministic auditable steps verifying live state; presenter narration is grounded without LLM improvisation | Demonstration Safety | Enforced by JudgeModeController and live verification |
| A-023 | Root .env loading occurs during server startup via python-dotenv with override=False; server-side permanent keys remain isolated from browser | Security & Operations | Verified by voice session broker tests and build bundle audits |


