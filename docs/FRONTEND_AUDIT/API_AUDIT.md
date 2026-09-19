# PLANT-X Frontend API Audit

## Summary
The frontend React application operates as a high-speed client-side simulation dashboard. While the Python backend exposes a complete REST API via FastAPI (`/api/plant/...`, `/api/foulx/...`), the frontend current build renders pre-compiled client-side telemetry in `mockData.ts` to ensure instantaneous UI rendering without HTTP latency during offline demonstration.

## Endpoints Inventory & Audit

| FRONTEND CALL | BACKEND ENDPOINT | METHOD | REQUEST PAYLOAD | RESPONSE DATA | COMPONENT | STATUS |
|---|---|---|---|---|---|---|
| `fetchPlantOverview()` | `/api/plant/overview` | `GET` | None | `{ status: "OPERATIONAL", units: [...] }` | `App.tsx` | `MOCKED_CLIENT_SIDE` |
| `fetchUnitDetails("E-102")` | `/api/plant/units/E-102` | `GET` | None | `{ fouling_resistance: 0.00042, ... }` | `PlantProcessOverlay.tsx` | `MOCKED_CLIENT_SIDE` |
| `runFoulXPrognosis()` | `/api/foulx/predict` | `POST` | `{ unit_id: "E-102", horizon: 30 }` | `{ forecast: [...], gate: "PASS" }` | `FoulXCopilot.tsx` | `MOCKED_CLIENT_SIDE` |
| `evaluateTrustGate()` | `/api/foulx/trust-gate` | `POST` | `{ stress_sigma: 6.0 }` | `{ gate: "ABSTAIN", regime: "OOD" }` | `TrustGateModal.tsx` | `MOCKED_CLIENT_SIDE` |
| `getEvidenceGraph()` | `/api/evidence/graph` | `GET` | `{ unit_id: "E-102" }` | `{ hypotheses: [...], evidence: [...] }` | `EvidenceOverlay.tsx` | `MOCKED_CLIENT_SIDE` |
| `calculateThermodynamics()`| `/api/thermo/calculate` | `POST` | `{ property_package: "IDEAL_GAS" }` | `{ eos: "UNSUPPORTED", transport: "UNAVAILABLE" }` | `ChemistryModal.tsx` | `MOCKED_CLIENT_SIDE` |

## Backend Endpoints Verification
- Backend FastAPI endpoints are defined in `src/plantx/api/` (`main.py`).
- Frontend is disconnected from HTTP endpoints and uses internal React state / `mockData.ts` handlers.
