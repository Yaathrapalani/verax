# PLANT-X / FOUL-X FINAL FEATURE ACCEPTANCE MATRIX

**Evaluated Baseline**: Git Commit `5d8abce51c46a7ac2c073761789b16ae2f45787a` (`v0.1.0-rc1`)  
**Environment**: Node v24.19.0, Python 3.11.16 (`.venv`)  
**Strict Acceptance Rule**: Every item must have exactly one status: `PASS`, `FAIL`, `BLOCKED`, `NOT_TESTED`. Zero vague terminology.

---

## Feature Acceptance Matrix

| Feature ID | Feature Domain | Truth State | Status | Reproducible Test Command | Evidence / Limitation |
|---|---|---|---|---|---|
| `FOULX_PHYSICS` | Heat Exchanger Thermal State & Rf Calculation | `DERIVED` | **PASS** | `pytest tests/physics/` | M2 physics thermal balance error < 1.2%. 523/523 backend tests pass. |
| `FOULX_RIDGE_FORECAST` | Ridge Temporal Forecast Model (alpha=100.0) | `DERIVED` | **PASS** | `pytest tests/test_foulx_ridge_forecast.py` | Predicts future Rf over 24h horizon with conformal intervals. |
| `FOULX_RELIABILITY_GATE` | Out-of-Distribution & Reliability Gate | `DERIVED` | **PASS** | `pytest tests/gate/test_safety.py` | Supported case: PASS; +6σ shifted regime: ABSTAIN (REGIME_OOD). |
| `FOULX_DECISION_FALLBACK` | Decision Engine & Fixed-Policy Fallback | `DERIVED` | **PASS** | `python scripts/gate15_foulx_verification.py` | Gate failure triggers ABSTAIN decision and falls back to fixed policy. |
| `CANONICAL_TOPOLOGY` | Crude Preheat Train Process Graph (P-101 to C-101) | `OBSERVED` | **PASS** | `npx -y tsx --test tests/workstation_test.ts` (Test 1, 3) | Equipment sequence topologically ordered. |
| `2D_3D_CROSS_VIEW_SYNC` | Identity Synchronization across 2D/Graph/3D | `DERIVED` | **PASS** | `npx -y tsx tests/gate16_sync_test.ts` | E-102 sync verified; asset switch to E-103 completely purges stale selection. |
| `3D_REPRESENTATIVE_CAD` | 3D Spatial Layout Projection & Epistemic Boundary | `REPRESENTATIVE` | **PASS** | `npx -y tsx tests/gate16_sync_test.ts` | Displays 'Representative Inferred Geometry — Not As-Built CAD'; CAD: UNAVAILABLE. |
| `TRUTH_FIREWALL` | Epistemic Boundary & Escalation Blocker | `DERIVED` | **PASS** | `npx -y tsx tests/gate14_truth_firewall.ts` | All 4 escalations (INFERRED, SIMULATED, UNAVAILABLE, REPRESENTATIVE -> OBSERVED) blocked. |
| `ACTUATOR_SAFETY` | Actuator & PLC/DCS Safety Boundary | `DERIVED` | **PASS** | `npx -y tsx tests/gate19_security_test.ts` | Open valve, Set pump speed, Change setpoint, Shutdown, Modify PLC/DCS rejected. |
| `BUNDLE_SECRETS_SCAN` | Production Dist Bundle Credentials Scan | `DERIVED` | **PASS** | `npx -y tsx tests/gate19_security_test.ts` | Zero API keys, secrets, private keys, or tokens detected in bundle. |
| `VOICE_BROWSER_PATH` | Browser SpeechRecognition Fallback | `DERIVED` | **PASS** | `npx -y tsx --test tests/workstation_test.ts` (Test 23, 65) | continuous=false, interimResults=false, onresult -> executeUtterance(). |
| `VOICE_ACOUSTIC_ISOLATION` | RealtimeAudio Feedback Prevention | `DERIVED` | **PASS** | `npx -y tsx --test tests/workstation_test.ts` (Test 66) | processorNode -> silentGain (gain=0) -> destination eliminates speaker loop. |
| `VOICE_GEMINI_LIVE` | Multimodal Live API WebSocket Broker | `DERIVED` | **BLOCKED** | Environment check (`echo $GEMINI_API_KEY`) | GEMINI_API_KEY absent in local runtime; gracefully displays NOT CONFIGURED. |
| `VOICE_INTERRUPTION_VAD` | Spoken Barge-In Interruption & Task Survival | `DERIVED` | **PASS** | `npx -y tsx tests/gate10_interruption.ts` | VAD stops speech in 0.18ms; background scenario timer survives. |
| `VOICE_CANCELLATION` | Disambiguation: "Cancel." vs "Stop speaking." | `DERIVED` | **PASS** | `npx -y tsx tests/gate11_cancellation.ts` | "Cancel." cancels timer; "Stop speaking." stops TTS only. Unambiguous. |
| `VOICE_CONTEXT_CHAIN` | Natural Multi-Turn Context Follow-Up | `DERIVED` | **PASS** | `npx -y tsx tests/gate9_context.ts` | 6-turn chain ("Show me E-102" -> "Why?" -> "What's missing?" -> etc.) verified. |
| `FACE_PRESENCE_PRIVACY` | Privacy-Preserving Face Presence Detector | `DERIVED` | **PASS** | `npx -y tsx tests/gate12_13_face_presence.ts` | Presence-only boolean; zero embeddings/templates/cloud/DB; default OFF. |
| `FACE_PRESENCE_DEBOUNCE` | Face Presence Debounce (3 hits / 5 misses) | `DERIVED` | **PASS** | `npx -y tsx tests/gate12_13_face_presence.ts` | 3 hits (450ms) to wake; 5 misses (750ms) to drop. Reconciled & verified. |
| `FACE_ONE_TURN_WAKE` | Single-Turn Voice Wake Activation | `DERIVED` | **PASS** | `npx -y tsx tests/gate12_13_face_presence.ts` | Triggers exactly once on confirmed presence; no continuous listening loop. |
| `JUDGE_MODE_19_STEPS` | Full 19-Step Deterministic Acceptance Walkthrough | `DERIVED` | **PASS** | `npx -y tsx tests/gate17_judge_run.ts` | All 19 steps executed and passed against real workstation state. |
| `BROWSER_AUTOMATION_E2E` | Live Browser Driver Interaction (Playwright) | `DERIVED` | **BLOCKED** | `npx -y playwright test` | Upstream CDN 404 prevented Playwright download. Driver unavailable. |
