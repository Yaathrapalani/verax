# F1 Live Verification Report

## Verification Checklist
- [x] FastAPI server running on `http://localhost:8000`
- [x] `/health` returns `healthy` status and checksum `c8ed7d9c...4b4d9`
- [x] `/api/replay/snapshot` returns deterministic data for `E02`
- [x] Frontend `F1LiveBindingDemo` component renders live data with `LIVE BACKEND CONNECTED` badge
- [x] Regime shift (+6σ) toggle transitions Trust Gate to `ABSTAIN — OOD DETECTED` with `FIXED POLICY ACTIVE`
