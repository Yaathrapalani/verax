# F1 Backend Endpoint Inventory

| METHOD | PATH | REQUEST SCHEMA | RESPONSE SCHEMA | SOURCE MODULE | STAGE | PURPOSE | CURRENT FRONTEND CONSUMER | STATUS |
|---|---|---|---|---|---|---|---|---|
| `GET` | `/health` | None | `{ status, service, version, artifacts_loaded, dataset_checksum, timestamp_range }` | `src.foulx.api.app` | S0 | Health & artifact integrity check | `PlantHeader` / Status Bar | `VERIFIED_LIVE` |
| `GET` | `/api/manifest` | None | `ReplayManifest` (min/max timestamp, total rows, dataset SHA) | `src.foulx.api.app` | S2 | Replay metadata & dataset integrity | `ProvenanceModal` / Status Bar | `VERIFIED_LIVE` |
| `GET` | `/api/exchangers` | None | `Dict[str, str]` (`{"E01": "E01 Crude/Heavy Naphtha", ...}`) | `src.foulx.api.app` | S3 | Supported exchanger registry | `PlantHeader` / Plant Explorer | `VERIFIED_LIVE` |
| `GET` | `/api/replay/snapshot` | `time_hr`, `exchanger_id`, `scenario` | `ReplaySnapshot` (telemetry, physics_state, forecast_state, reliability_state, decision_state, evidence_reference) | `src.foulx.api.app` | S2–S10 | Deterministic temporal evidence snapshot & prognosis | `PlantClientState` Hydrator | `VERIFIED_LIVE` |
| `GET` | `/api/simulation/frame` | `time_hr`, `exchanger_id`, `scenario`, `shifted` | `SimulationFrame` | `src.foulx.api.app` | S9/S14 | Simulation frame execution | `SimulationWorkspace` | `VERIFIED_LIVE` |
| `POST` | `/api/simulation/clean` | `time_hr`, `exchanger_id` | `SimulationFrame` | `src.foulx.api.app` | S10/S14 | Simulated cleaning trigger | `SimulationWorkspace` | `VERIFIED_LIVE` |
